#!/usr/bin/env python3
"""
GUI deployment helper for the Server Data Collector on Linux targets.

The app is intentionally dependency-light: it uses Python's standard-library
Tkinter GUI and the system ssh/scp clients. Password authentication is supported
when sshpass is installed locally; SSH keys are preferred.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "Server Data Collector Linux Deployer"
DEFAULT_API_ENDPOINT = "https://serverdashboard.elements.local/update"
DEFAULT_IMAGE = "felipema/server-data-collector:latest"
DEFAULT_REMOTE_DIR = "/opt/server-data-collector"
DEFAULT_CERT_DIR = "/opt/certs"
DEFAULT_SERVICE_NAME = "server-data-collector"
LOG_PATH = Path.home() / ".server-data-collector-deployer.log"


class DeployError(RuntimeError):
    """Raised when a deployment step fails."""


class DeploymentApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("940x760")
        self.root.minsize(850, 650)

        self.vars: dict[str, tk.Variable] = {
            "host": tk.StringVar(),
            "ssh_user": tk.StringVar(value="root"),
            "ssh_port": tk.StringVar(value="22"),
            "auth_mode": tk.StringVar(value="key"),
            "ssh_key": tk.StringVar(),
            "ssh_password": tk.StringVar(),
            "sudo_password": tk.StringVar(),
            "root_crt": tk.StringVar(),
            "api_endpoint": tk.StringVar(value=DEFAULT_API_ENDPOINT),
            "server_id": tk.StringVar(),
            "rack_location": tk.StringVar(),
            "connection": tk.StringVar(value="U.2"),
            "drive_bays": tk.StringVar(value="8"),
            "region": tk.StringVar(value="Rancho Cordova"),
            "image": tk.StringVar(value=DEFAULT_IMAGE),
            "remote_dir": tk.StringVar(value=DEFAULT_REMOTE_DIR),
            "cert_dir": tk.StringVar(value=DEFAULT_CERT_DIR),
            "service_name": tk.StringVar(value=DEFAULT_SERVICE_NAME),
            "install_docker": tk.BooleanVar(value=True),
            "enable_service": tk.BooleanVar(value=True),
            "start_service": tk.BooleanVar(value=True),
        }
        self._build_ui()
        self.log(f"Log file: {LOG_PATH}")

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill=tk.BOTH, expand=True)

        form = ttk.Frame(outer)
        form.pack(fill=tk.X)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        row = 0
        self._entry(form, row, "Target IP / host", "host", required=True)
        self._entry(form, row, "SSH user", "ssh_user", col=2)
        row += 1
        self._entry(form, row, "SSH port", "ssh_port")
        self._combo(form, row, "Authentication", "auth_mode", ("key", "password"), col=2)
        row += 1
        self._file_entry(form, row, "SSH key", "ssh_key", filetypes=(("SSH keys", "*"),))
        self._secret_entry(form, row, "SSH password", "ssh_password", col=2)
        row += 1
        self._secret_entry(form, row, "Sudo password", "sudo_password")
        self._file_entry(form, row, "root.crt", "root_crt", col=2, filetypes=(("Certificate", "*.crt"), ("All files", "*")))
        row += 1
        self._entry(form, row, "API endpoint", "api_endpoint", span=3, required=True)
        row += 1
        self._entry(form, row, "Server ID", "server_id", required=True)
        self._entry(form, row, "Rack location", "rack_location", col=2, required=True)
        row += 1
        self._entry(form, row, "Connection", "connection")
        self._entry(form, row, "Drive bays", "drive_bays", col=2)
        row += 1
        self._entry(form, row, "Region", "region")
        self._entry(form, row, "Container image", "image", col=2)
        row += 1
        self._entry(form, row, "Remote app dir", "remote_dir")
        self._entry(form, row, "Remote cert dir", "cert_dir", col=2)
        row += 1
        self._entry(form, row, "systemd service", "service_name")

        options = ttk.LabelFrame(outer, text="Deployment options", padding=8)
        options.pack(fill=tk.X, pady=(10, 8))
        ttk.Checkbutton(options, text="Install Docker if missing (Rocky/RHEL/CentOS/Fedora via dnf)", variable=self.vars["install_docker"]).pack(anchor=tk.W)
        ttk.Checkbutton(options, text="Enable systemd service at boot", variable=self.vars["enable_service"]).pack(anchor=tk.W)
        ttk.Checkbutton(options, text="Start/restart the collector after deployment", variable=self.vars["start_service"]).pack(anchor=tk.W)

        buttons = ttk.Frame(outer)
        buttons.pack(fill=tk.X, pady=(0, 8))
        self.deploy_button = ttk.Button(buttons, text="Deploy", command=self.deploy)
        self.deploy_button.pack(side=tk.LEFT)
        ttk.Button(buttons, text="Validate only", command=lambda: self.deploy(validate_only=True)).pack(side=tk.LEFT, padx=8)
        ttk.Button(buttons, text="Clear log", command=lambda: self.log_text.delete("1.0", tk.END)).pack(side=tk.LEFT)

        log_frame = ttk.LabelFrame(outer, text="Step log", padding=8)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=18)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def _entry(self, parent: ttk.Frame, row: int, label: str, key: str, col: int = 0, span: int = 1, required: bool = False) -> None:
        text = f"{label}{' *' if required else ''}"
        ttk.Label(parent, text=text).grid(row=row, column=col, sticky=tk.W, padx=(0, 6), pady=4)
        ttk.Entry(parent, textvariable=self.vars[key]).grid(row=row, column=col + 1, columnspan=span, sticky=tk.EW, pady=4)

    def _secret_entry(self, parent: ttk.Frame, row: int, label: str, key: str, col: int = 0) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=col, sticky=tk.W, padx=(0, 6), pady=4)
        ttk.Entry(parent, textvariable=self.vars[key], show="*").grid(row=row, column=col + 1, sticky=tk.EW, pady=4)

    def _combo(self, parent: ttk.Frame, row: int, label: str, key: str, values: tuple[str, ...], col: int = 0) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=col, sticky=tk.W, padx=(0, 6), pady=4)
        ttk.Combobox(parent, textvariable=self.vars[key], values=values, state="readonly").grid(row=row, column=col + 1, sticky=tk.EW, pady=4)

    def _file_entry(self, parent: ttk.Frame, row: int, label: str, key: str, col: int = 0, filetypes: tuple[tuple[str, str], ...] = (("All files", "*"),)) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=col, sticky=tk.W, padx=(0, 6), pady=4)
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col + 1, sticky=tk.EW, pady=4)
        frame.columnconfigure(0, weight=1)
        ttk.Entry(frame, textvariable=self.vars[key]).grid(row=0, column=0, sticky=tk.EW)
        ttk.Button(frame, text="Browse", command=lambda: self._browse_file(key, filetypes)).grid(row=0, column=1, padx=(6, 0))

    def _browse_file(self, key: str, filetypes: tuple[tuple[str, str], ...]) -> None:
        selected = filedialog.askopenfilename(filetypes=filetypes)
        if selected:
            self.vars[key].set(selected)

    def log(self, message: str) -> None:
        stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{stamp}] {message}\n"
        def append() -> None:
            self.log_text.insert(tk.END, line)
            self.log_text.see(tk.END)
        if hasattr(self, "log_text"):
            self.root.after(0, append)
        with LOG_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write(line)

    def deploy(self, validate_only: bool = False) -> None:
        try:
            config = self._validate()
        except DeployError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        self.deploy_button.configure(state=tk.DISABLED)
        thread = threading.Thread(target=self._deploy_worker, args=(config, validate_only), daemon=True)
        thread.start()

    def _validate(self) -> dict[str, str | bool]:
        config = {key: var.get() for key, var in self.vars.items()}
        for key in ("host", "ssh_user", "ssh_port", "api_endpoint", "server_id", "rack_location", "root_crt"):
            if not str(config[key]).strip():
                raise DeployError(f"Missing required field: {key.replace('_', ' ')}")
        cert = Path(str(config["root_crt"])).expanduser()
        if not cert.is_file():
            raise DeployError("The selected root.crt file does not exist.")
        if config["auth_mode"] == "key":
            key_path = str(config["ssh_key"]).strip()
            if key_path and not Path(key_path).expanduser().is_file():
                raise DeployError("The selected SSH key file does not exist.")
        else:
            if not str(config["ssh_password"]).strip():
                raise DeployError("SSH password is required when password authentication is selected.")
            if shutil.which("sshpass") is None:
                raise DeployError("Password authentication requires sshpass installed locally. Use SSH key auth or install sshpass.")
        if shutil.which("ssh") is None or shutil.which("scp") is None:
            raise DeployError("This script requires the system ssh and scp commands.")
        return config

    def _deploy_worker(self, config: dict[str, str | bool], validate_only: bool) -> None:
        try:
            self.log("Starting validation")
            self._run_remote(config, "echo connected")
            self.log("SSH connection succeeded")
            if validate_only:
                self.log("Validation complete; no remote changes were made")
                return

            remote_dir = str(config["remote_dir"]).rstrip("/")
            cert_dir = str(config["cert_dir"]).rstrip("/")
            service_name = str(config["service_name"]).strip()
            compose_remote = f"{remote_dir}/docker-compose.yml"
            cert_remote = f"{cert_dir}/root.crt"
            service_remote = f"/etc/systemd/system/{service_name}.service"

            self.log("Creating remote directories")
            self._run_sudo(config, f"mkdir -p {shlex.quote(remote_dir)} {shlex.quote(cert_dir)}")

            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                compose_file = tmp_path / "docker-compose.yml"
                service_file = tmp_path / f"{service_name}.service"
                compose_file.write_text(self._compose_yaml(config), encoding="utf-8")
                service_file.write_text(self._systemd_unit(remote_dir, service_name), encoding="utf-8")

                self.log("Uploading root.crt")
                self._scp(config, str(config["root_crt"]), f"/tmp/root.crt.{os.getpid()}")
                self._run_sudo(config, f"install -m 0644 /tmp/root.crt.{os.getpid()} {shlex.quote(cert_remote)} && rm -f /tmp/root.crt.{os.getpid()}")

                self.log("Uploading docker-compose.yml")
                self._scp(config, str(compose_file), f"/tmp/docker-compose.yml.{os.getpid()}")
                self._run_sudo(config, f"install -m 0644 /tmp/docker-compose.yml.{os.getpid()} {shlex.quote(compose_remote)} && rm -f /tmp/docker-compose.yml.{os.getpid()}")

                self.log("Uploading systemd service")
                self._scp(config, str(service_file), f"/tmp/{service_name}.service.{os.getpid()}")
                self._run_sudo(config, f"install -m 0644 /tmp/{service_name}.service.{os.getpid()} {shlex.quote(service_remote)} && rm -f /tmp/{service_name}.service.{os.getpid()}")

            if config["install_docker"]:
                self.log("Checking Docker installation")
                self._run_sudo(config, self._docker_install_command())

            self.log("Reloading systemd")
            self._run_sudo(config, "systemctl daemon-reload")
            if config["enable_service"]:
                self.log("Enabling collector service")
                self._run_sudo(config, f"systemctl enable {shlex.quote(service_name)}")
            if config["start_service"]:
                self.log("Starting collector service")
                self._run_sudo(config, f"systemctl restart {shlex.quote(service_name)}")
                self.log("Collecting service status")
                self._run_sudo(config, f"systemctl --no-pager --full status {shlex.quote(service_name)} || true")
            self.log("Deployment completed successfully")
            self.root.after(0, lambda: messagebox.showinfo(APP_TITLE, "Deployment completed successfully."))
        except Exception as exc:  # noqa: BLE001 - all exceptions must be logged in the GUI
            self.log(f"ERROR: {exc}")
            self.log(traceback.format_exc())
            self.root.after(0, lambda exc=exc: messagebox.showerror(APP_TITLE, f"Deployment failed: {exc}"))
        finally:
            self.root.after(0, lambda: self.deploy_button.configure(state=tk.NORMAL))

    def _base_ssh(self, config: dict[str, str | bool]) -> list[str]:
        cmd = ["ssh", "-p", str(config["ssh_port"]), "-o", "StrictHostKeyChecking=accept-new"]
        if config["auth_mode"] == "key" and str(config["ssh_key"]).strip():
            cmd.extend(["-i", str(Path(str(config["ssh_key"])).expanduser())])
        return cmd

    def _base_scp(self, config: dict[str, str | bool]) -> list[str]:
        cmd = ["scp", "-P", str(config["ssh_port"]), "-o", "StrictHostKeyChecking=accept-new"]
        if config["auth_mode"] == "key" and str(config["ssh_key"]).strip():
            cmd.extend(["-i", str(Path(str(config["ssh_key"])).expanduser())])
        return cmd

    def _with_password(self, config: dict[str, str | bool], cmd: list[str]) -> list[str]:
        if config["auth_mode"] == "password":
            return ["sshpass", "-p", str(config["ssh_password"]), *cmd]
        return cmd

    def _target(self, config: dict[str, str | bool]) -> str:
        return f"{config['ssh_user']}@{config['host']}"

    def _run_remote(self, config: dict[str, str | bool], command: str, stdin: str | None = None) -> str:
        full_cmd = self._with_password(config, [*self._base_ssh(config), self._target(config), command])
        safe_cmd = self._redacted(full_cmd)
        self.log(f"RUN remote: {safe_cmd}")
        proc = subprocess.run(full_cmd, input=stdin, text=True, capture_output=True, check=False)
        if proc.stdout.strip():
            self.log(proc.stdout.strip())
        if proc.stderr.strip():
            self.log(proc.stderr.strip())
        if proc.returncode != 0:
            raise DeployError(f"Remote command failed with exit code {proc.returncode}: {command}")
        return proc.stdout

    def _run_sudo(self, config: dict[str, str | bool], command: str) -> str:
        if str(config["ssh_user"]) == "root":
            return self._run_remote(config, command)
        sudo_password = str(config["sudo_password"])
        if sudo_password:
            return self._run_remote(config, f"sudo -S -p '' bash -lc {shlex.quote(command)}", stdin=f"{sudo_password}\n")
        return self._run_remote(config, f"sudo bash -lc {shlex.quote(command)}")

    def _scp(self, config: dict[str, str | bool], source: str, remote_path: str) -> None:
        full_cmd = self._with_password(config, [*self._base_scp(config), source, f"{self._target(config)}:{remote_path}"])
        safe_cmd = self._redacted(full_cmd)
        self.log(f"RUN copy: {safe_cmd}")
        proc = subprocess.run(full_cmd, text=True, capture_output=True, check=False)
        if proc.stdout.strip():
            self.log(proc.stdout.strip())
        if proc.stderr.strip():
            self.log(proc.stderr.strip())
        if proc.returncode != 0:
            raise DeployError(f"File copy failed with exit code {proc.returncode}: {source}")

    def _redacted(self, cmd: list[str]) -> str:
        safe = list(cmd)
        for idx, value in enumerate(safe[:-1]):
            if value == "-p" and idx > 0 and safe[idx - 1] == "sshpass":
                safe[idx + 1] = "********"
        return " ".join(shlex.quote(part) for part in safe)

    def _compose_yaml(self, config: dict[str, str | bool]) -> str:
        env = {
            "API_ENDPOINT": config["api_endpoint"],
            "SERVER_ID": config["server_id"],
            "RACK_LOCATION": config["rack_location"],
            "CONNECTION": config["connection"],
            "DRIVE_BAYS": config["drive_bays"],
            "REGION": config["region"],
        }
        env_lines = "\n".join(json.dumps(f"{key}={value}") for key, value in env.items())
        env_lines = "\n".join(f"      - {line}" for line in env_lines.splitlines())
        cert_dir = str(config["cert_dir"]).rstrip("/")
        image = json.dumps(str(config["image"]))
        cert_volume = json.dumps(f"{cert_dir}:{cert_dir}:ro")
        return f"""services:
  server-data-container:
    image: {image}
    container_name: server-data-container
    privileged: true
    network_mode: "host"
    volumes:
      - /dev:/dev
      - /etc/os-release:/etc/os-release:ro
      - {cert_volume}
    environment:
{env_lines}
    restart: "no"
"""

    def _systemd_unit(self, remote_dir: str, service_name: str) -> str:
        return f"""[Unit]
Description=Server Data Collector ({service_name})
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory={remote_dir}
ExecStart=/bin/bash -lc 'docker compose up -d'
ExecStop=/bin/bash -lc 'docker compose down'
RemainAfterExit=yes
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
"""

    def _docker_install_command(self) -> str:
        return r"""
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  echo 'Docker and Docker Compose plugin already installed.'
else
  if command -v dnf >/dev/null 2>&1; then
    dnf -y install dnf-plugins-core
    dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo || \
      dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    dnf -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  else
    echo 'Automatic Docker installation currently supports dnf-based Linux distributions.' >&2
    exit 20
  fi
fi
systemctl enable --now docker
"""


def main() -> int:
    root = tk.Tk()
    DeploymentApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())

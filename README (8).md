# Server Data Collector Project

This project sets up a Python script to collect data from a server and send it to the infrastructure server using the push model. The script collects the server's system information and sends it to the infrastructure server, which stores and displays the most recent data.

## Table of Contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [PRC Setup](#prc-setup)

## General info
The server data collector script collects the following system information:
* Server Name
* Server Model
* Operating System
* CPU Model
* RAM
* Drive Bays
* Connection
* Rack Location
* IP Address
* Last Updated

The script sends the collected data to the infrastructure server using the push model.

## Technologies
Project is created with:
* Python version: 3.9-slim
* Docker version: 27.3.1
* Certifi version: 2024.8.30
* Charset-normalizer version: 3.3.2
* Idna version: 3.8
* Psutil version: 6.0.0
* Pyyaml version: 6.0.2
* Requests version: 2.32.3
* Urllib3 version: 2.2.2

## Setup

### Interactive Linux deployer

You can deploy the collector from an interactive shell instead of typing every option on the command line. Put your local certificate at the preferred path below, then run the Python deployer and press Enter to accept any default shown in brackets.

```bash
mkdir -p certs
cp root.crt certs/root.crt
python3 deploy_server_data_collector_gui.py
```

The deployer also accepts `--interactive` explicitly:

```bash
python3 deploy_server_data_collector_gui.py --interactive
```

The prompt asks for the target host, SSH login method, server ID, rack location, Docker/service options, and whether to validate SSH only. It defaults the local certificate path to `certs/root.crt`; if that file is not present, it also checks for `root.crt` in the project root.

### Windows
Docker is not supported on Windows Server. Instead this Program is ran via batch file.

To run this project, install Python locally using the following link:

```bash
https://www.python.org/downloads/
```

After installing Python, create the following directories for certificate and Project Code:

```bash
mkdir C:\Projects
mkdir C:\Certs
```

After creating the Project folder, retrieve the code from Felipe Martinez.
After creating the Certs folder, retrieve the root certificat from Felipe Martinez.

After retrieving the code, create a virtual environment using the following command:

```bash
cd C:\Projects\server-data-collector
python -m venv venv
```

After creating the virtual environment, install the required packages using the following command:

```bash
C:\Projects\server-data-collector\venv\Scripts\activate
pip install -r C:\Projects\server-data-collector\requirements.txt
```

After installing the required packages, modify the batch file using the following command:

```bash
notepad C:\Projects\server-data-collector\run.bat
```

Below is an example of the batch file:

```bash
@echo off
REM Set environment variables using the correct syntax for batch files
set API_ENDPOINT=http://serverdashboard.elements.local/update
set SERVER_ID=Test Server
set RACK_LOCATION=SAC 115B - Rack 1
set CONNECTION=U.2
set DRIVE_BAYS=8
set REGION=Rancho Cordova

REM Activate the virtual environment
call C:\Projects\server-data-collector\venv\Scripts\activate.bat

REM Run the Python script
python C:\Projects\server-data-collector\send_data.py

REM Deactivate the virtual environment
deactivate
```

After modifying the batch file, ensure the batch file posts information to the Dashboard API.

```bash
C:\Projects\server-data-collector\run.bat
```

Setting up the task scheduler to run the batch file.
* Open the Windows Start menu.
* Search for Task Scheduler and open it.
* Create Task.

General Tab:
* Name the task "Server Data Collector".
* Enable "Run whether user is logged on or not".
* Enable "Run with highest privileges".

Triggers Tab:
* Click "New".
* Begin the task "At startup".

Actions Tab:
* Click "New".
* Action: Start a program.
* Program/script: C:\Projects\server-data-collector\run.bat
* Click "OK".

Conditions Tab:
* Uncheck "Start the task only if the computer is on AC power".

Settings Tab:
* Uncheck "Stop the task if it runs longer than".
* Click "OK".

After setting up the task scheduler, perform a Restart to ensure the task runs at startup.



### Ubuntu
To run this project, install docker locally using the following link:

```bash
https://docs.docker.com/engine/install/ubuntu/
```

After installing docker, create a directory for the root certificate, and place the root certificate in the /opt/certs directory. (Retrieve from Felipe Martinez)
:
```bash
sudo mkdir -p /opt/certs
sudo cp root.crt /opt/certs/
```


After installing the root certificate, create a docker-compose.yml file using the following command:

```bash
sudo nano /opt/docker-compose.yml
```

Copy and paste the following code into the docker-compose.yml file:

```bash
services:
  server-data-container:
    image: felipema/server-data-collector:latest
    container_name: server-data-container
    privileged: true
    network_mode: "host"
    volumes:
      - /dev:/dev
      - /etc/os-release:/etc/os-release:ro
      - /opt/certs:/opt/certs
    environment:
      - API_ENDPOINT=https://serverdashboard.elements.local/update
      - SERVER_ID=SERVER
      - RACK_LOCATION=RACK-LOCATION
      - CONNECTION=U.2
      - DRIVE_BAYS=8
      - REGION=Rancho Cordova
    restart: "no"  # Temporarily disable restart for debugging
```

After creating the docker-compose.yml file, create a systemd service file using the following command:
```bash
sudo nano /etc/systemd/system/docker-compose-app.service
```

Copy and paste the following code into the docker-compose-app.service file:
```bash
[Unit]
Description=Docker Compose Application Service
Requires=docker.service
After=docker.service

[Service]
WorkingDirectory=/opt
ExecStart=/bin/bash -c "/usr/bin/docker compose up -d"
ExecStop=/bin/bash -c "/usr/bin/docker compose down"
User=root
Group=root
TimeoutStartSec=0
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

After creating the docker-compose-app.service file, reload the systemd daemon using the following command:
```bash
sudo systemctl daemon-reload
```

After reloading the systemd daemon, start the docker-compose-app service using the following command:
```bash
sudo systemctl start docker-compose-app
sudo systemctl enable docker-compose-app
```


### CentOS
To run this project, install docker locally using the following link:

```bash
https://docs.docker.com/engine/install/centos/
```

After installing docker, create a directory for the root certificate, and place the root certificate in the /opt/certs directory. (Retrieve from Felipe Martinez)
:
```bash
sudo mkdir -p /opt/certs
sudo cp root.crt /opt/certs/
```

After installing the root certificate, run the following commands:

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

After installing docker, create the docker-compose.yml file using the following command:

```bash
sudo nano /opt/docker-compose.yml
```

Copy and paste the following code into the docker-compose.yml file:

```bash
services:
  server-data-container:
    image: felipema/server-data-collector:latest
    container_name: server-data-container
    privileged: true
    network_mode: "host"
    volumes:
      - /dev:/dev
      - /etc/os-release:/etc/os-release:ro
      - /opt/certs:/opt/certs
    environment:
      - API_ENDPOINT=https://serverdashboard.elements.local/update
      - SERVER_ID=SERVER
      - RACK_LOCATION=RACK-LOCATION
      - CONNECTION=U.2
      - DRIVE_BAYS=8
      - REGION=Rancho Cordova
    restart: "no"  # Temporarily disable restart for debugging
```

After creating the docker-compose.yml file, create a systemd service file using the following command:

```bash
sudo nano /etc/systemd/system/docker-compose-app.service
```

Copy and paste the following code into the docker-compose-app.service file:

```bash
[Unit]
Description=Docker Compose Application Service
Requires=docker.service
After=docker.service

[Service]
WorkingDirectory=/opt
ExecStart=/bin/bash -c "/usr/bin/docker compose up -d"
ExecStop=/bin/bash -c "/usr/bin/docker compose down"
User=root
Group=root
TimeoutStartSec=0
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

After creating the docker-compose-app.service file, reload the systemd daemon using the following command:

```bash
sudo systemctl daemon-reload
```

After reloading the systemd daemon, start the docker-compose-app service using the following command:

```bash
sudo systemctl start docker-compose-app
sudo systemctl enable docker-compose-app
```

### Fedora Linux
To run this project, install docker locally using the following link:
```bash
https://docs.docker.com/engine/install/fedora/
```

After installing docker, create a directory for the root certificate, and place the root certificate in the /opt/certs directory. (Retrieve from Felipe Martinez)
```bash
sudo mkdir -p /opt/certs
sudo cp root.crt /opt/certs/
```

After installing the root certificate, create the docker-compose.yml file using the following command:

```bash
sudo nano /opt/docker-compose.yml
```

Copy and paste the following code into the docker-compose.yml file:
```bash
services:
  server-data-container:
    image: felipema/server-data-collector:latest
    container_name: server-data-container
    privileged: true
    network_mode: "host"
    volumes:
      - /dev:/dev
      - /etc/os-release:/etc/os-release:ro
      - /opt/certs:/opt/certs
    environment:
      - API_ENDPOINT=https://serverdashboard.elements.local/update
      - SERVER_ID=SERVER
      - RACK_LOCATION=RACK-LOCATION
      - CONNECTION=U.2
      - DRIVE_BAYS=8
      - REGION=Rancho Cordova
    restart: "no"  # Temporarily disable restart for debugging
```

After creating the docker-compose.yml file, create a systemd service file using the following command:

```bash
sudo nano /etc/systemd/system/docker-compose-app.service
```

Copy and paste the following code into the docker-compose-app.service file:

```bash
[Unit]
Description=Docker Compose Application Service
Requires=docker.service
After=docker.service

[Service]
WorkingDirectory=/opt
ExecStart=/bin/bash -c "/usr/bin/docker compose up -d"
ExecStop=/bin/bash -c "/usr/bin/docker compose down"
User=root
Group=root
TimeoutStartSec=0
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

After creating the docker-compose-app.service file, reload the systemd daemon using the following command:

```bash
sudo systemctl daemon-reload
```

After reloading the systemd daemon, start the docker-compose-app service using the following command:

```bash
sudo systemctl start docker-compose-app
sudo systemctl enable docker-compose-app
```





### Rocky Linux 
To run this project, install docker locally using the following link:

```bash
https://docs.docker.com/engine/install/rhel/
```

After installing docker, create a directory for the root certificate, and place the root certificate in the /opt/certs directory. (Retrieve from Felipe Martinez)
:
```bash
sudo mkdir -p /opt/certs
sudo cp root.crt /opt/certs/
```

After installing the root certificate, create the docker-compose.yml file using the following command:

```bash
sudo nano /opt/docker-compose.yml
```

Copy and paste the following code into the docker-compose.yml file:
```bash
services:
  server-data-container:
    image: felipema/server-data-collector:latest
    container_name: server-data-container
    privileged: true
    network_mode: "host"
    volumes:
      - /dev:/dev
      - /etc/os-release:/etc/os-release:ro
      - /opt/certs:/opt/certs
    environment:
      - API_ENDPOINT=https://serverdashboard.elements.local/update
      - SERVER_ID=SERVER
      - RACK_LOCATION=RACK-LOCATION
      - CONNECTION=U.2
      - DRIVE_BAYS=8
      - REGION=Rancho Cordova
    restart: "no"  # Temporarily disable restart for debugging
```

After creating the docker-compose.yml file, create a systemd service file using the following command:

```bash
sudo nano /etc/systemd/system/docker-compose-app.service
```

Copy and paste the following code into the docker-compose-app.service file:

```bash
[Unit]
Description=Docker Compose Application Service
Requires=docker.service
After=docker.service

[Service]
WorkingDirectory=/opt
ExecStart=/bin/bash -c "/usr/bin/docker compose up -d"
ExecStop=/bin/bash -c "/usr/bin/docker compose down"
User=root
Group=root
TimeoutStartSec=0
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

After creating the docker-compose-app.service file, reload the systemd daemon using the following command:

```bash
sudo systemctl daemon-reload
```

After reloading the systemd daemon, start the docker-compose-app service using the following command:

```bash
sudo systemctl start docker-compose-app
sudo systemctl enable docker-compose-app
```

## PRC Setup
To run this project, install docker locally using the following link:

```bash
https://docs.docker.com/engine/install
```

After installing docker, create a directory for the root certificate, and place the root certificate in the /opt/certs directory. (Retrieve from Felipe Martinez)

```bash
sudo mkdir -p /opt/certs
sudo cp root.crt /opt/certs/
```

After installing the root certificate, create the docker-compose.yml file using the following command:

```bash
sudo nano /opt/docker-compose.yml
```

Copy and paste the following code into the docker-compose.yml file:

```bash
services:
  server-data-container:
    image: 10.74.26.9:5050/server-data-collector:latest 
    container_name: server-data-container
    privileged: true
    network_mode: "host"
    volumes:
      - /dev:/dev
      - /etc/os-release:/etc/os-release:ro
      - /opt/certs:/opt/certs
    environment:
      - API_ENDPOINT=https://serverdashboard.elements.local/update
      - SERVER_ID=SERVER
      - RACK_LOCATION=RACK-LOCATION
      - CONNECTION=U.2
      - DRIVE_BAYS=8
      - REGION=Rancho Cordova
    restart: "no"  # Temporarily disable restart for debugging
```

Add the following regirstry to the docker daemon.json file:
(If there exists data in the file, feel free to delete the previous data or append)

```bash
{
    "insecure-registries" : ["10.74.26.9:5050"]
}
```

Restart the docker service using the following command:

```bash
sudo systemctl restart docker
```

Create a systemd service file using the following command:

```bash
[Unit]
Description=Docker Compose Application Service
Requires=docker.service
After=docker.service

[Service]
WorkingDirectory=/opt
ExecStart=/bin/bash -c "/usr/bin/docker compose up -d"
ExecStop=/bin/bash -c "/usr/bin/docker compose down"
User=root
Group=root
TimeoutStartSec=0
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

After creating the docker-compose-app.service file, reload the systemd daemon using the following command:

```bash
sudo systemctl daemon-reload
```

After reloading the systemd daemon, start the docker-compose-app service using the following command:

```bash
sudo systemctl start docker-compose-app
sudo systemctl enable docker-compose-app
```

## Linux CLI/GUI Deployer

Use `deploy_server_data_collector_gui.py` when you want to deploy or update the collector on a Linux server without manually signing in and typing each setup command. The same script works from a command line on headless Linux systems and can also open a Tkinter GUI on desktop Linux systems. It is designed for Rocky Linux first, while also working with other SSH-accessible Linux targets that already have Docker or use a compatible `dnf` package manager.

### What it does

* Accepts the target IP or hostname, SSH username, SSH key or password details, sudo password when needed, server metadata, container image, API endpoint, and the `root.crt` file from command-line flags or GUI fields.
* Copies `root.crt` to the target certificate directory.
* Creates the remote `docker-compose.yml` with the values entered in the command line or GUI.
* Creates and reloads a systemd service for the collector.
* Optionally installs Docker and the Docker Compose plugin on Rocky/RHEL/CentOS/Fedora-style systems using `dnf`.
* Optionally enables the service at boot and starts/restarts it immediately.
* Logs every step to stdout in CLI mode, to the GUI in GUI mode, and always appends the same log to `~/.server-data-collector-deployer.log` on the machine running the deployer.

### Requirements on the machine running the deployer

For command-line mode, install Python and SSH clients:

```bash
sudo dnf install -y python3 openssh-clients
```

For GUI mode, install Tkinter as well:

```bash
sudo dnf install -y python3-tkinter
```

SSH-key authentication is recommended. If you must use SSH password authentication, install `sshpass` as well:

```bash
sudo dnf install -y sshpass
```

### Run from command line on a headless server

Use `--validate-only` first to confirm SSH access without changing the target:

```bash
python3 deploy_server_data_collector_gui.py \
  --host 192.0.2.25 \
  --ssh-user root \
  --ssh-key ~/.ssh/id_rsa \
  --root-crt ./root.crt \
  --server-id SERVER01 \
  --rack-location "SAC 115B - Rack 1" \
  --validate-only
```

Then run the full deployment:

```bash
python3 deploy_server_data_collector_gui.py \
  --host 192.0.2.25 \
  --ssh-user root \
  --ssh-key ~/.ssh/id_rsa \
  --root-crt ./root.crt \
  --server-id SERVER01 \
  --rack-location "SAC 115B - Rack 1" \
  --connection U.2 \
  --drive-bays 8 \
  --region "Rancho Cordova"
```

If you need password authentication instead of SSH keys, use `--auth-mode password --ask-ssh-password` so the password is prompted securely instead of stored in shell history. If you connect as a non-root user that needs sudo, add `--ask-sudo-password`.

Useful command-line switches:

* `--no-install-docker` skips Docker installation if the target already has Docker.
* `--no-enable-service` creates the service but does not enable it at boot.
* `--no-start-service` deploys files but does not start or restart the collector.
* `--help` shows every available option.

### Run with the GUI on a desktop Linux system

```bash
python3 deploy_server_data_collector_gui.py --gui
```

1. Enter the target server IP or DNS name.
2. Select key or password authentication.
3. Fill in the collector fields such as API endpoint, server ID, rack location, connection type, drive bays, region, and image.
4. Click **Browse** beside `root.crt` and select the certificate file.
5. Leave **Install Docker if missing** checked for new Rocky Linux targets.
6. Click **Validate only** to test SSH connectivity without changing the target, or click **Deploy** to perform the full installation.

If a step fails, the failure is logged with the command output so you can correct credentials, sudo access, network connectivity, package repositories, or Docker issues and run the deployer again.

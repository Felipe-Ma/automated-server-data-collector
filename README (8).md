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

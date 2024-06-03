# HSLU PREN Team 03

## Table of Contents

* [Installation](#installation)
* [Configuration](#configuration)
* [Deployment](#deployment)
* [Development](#development)
    * [Code Quality Check](#code-quality-check)
    * [Unit Tests](#unit-tests)
    * [Local UART Setup](#local-uart-setup)

## Installation

Clone the git repository and move it to `/opt/pren`:

```shell
git clone https://<PAT>@github.com/lorinbucher/hslu-pren.git
sudo mv hslu-pren /opt/pren
sudo chown ${USER}:${USER} /opt/pren
```

Initialize a virtual python environment and install the necessary dependencies:

```shell
# create virtual environment
python3 -m venv /opt/pren/venv
# initialize virtual environment
source /opt/pren/venv/bin/activate
# install dependencies
python3 -m pip install -r /opt/pren/requirements.txt
```

## Configuration

```toml
# /opt/pren/config.toml
[api]
address = "oawz3wjih1.execute-api.eu-central-1.amazonaws.com"
team_nr = "03"
token = "<auth_token>"

[rtsp]
address = "147.88.48.131"
user = "pren"
password = "<password>"
profile = "pren_profile_med" # pren_profile_small

[serial]
baud_rate = 115200
read = "/dev/ttyAMA0"
write = "/dev/ttyAMA0"

[app]
confidence = 25
recognition_timeout = 60
incremental_build = false
efficiency_mode = false
```

## Deployment

The 3D Re-Builder application is deployed with `systemd`:

```shell
sudo mkdir -p /usr/local/lib/systemd/system
sudo cp /opt/pren/pren-rebuilder.service /usr/local/lib/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable pren-rebuilder.service
sudo systemctl start pren-rebuilder.service
```

The application logs can be accessed using `journalctl`:

```shell
sudo journalctl -u pren-rebuilder.service -f
```

To automatically start the chromium browser with the website, add the following line:

X11:

```shell
# /etc/xdg/lxsession/LXDE-pi/autostart
/opt/pren/chromium_start.sh
```

Wayland:

```shell
# /home/$USER/.config/wayfire.ini
[autostart]
runme = /opt/pren/chromium_start.sh
```

## Development

### Code Quality Check

```shell
source venv/bin/activate
mypy .
pylint . --recursive=yes --verbose
```

### Unit Tests

Note: The test methods have to be called test or else they won't run after this command.

```shell
python3 -m unittest
```

### Local UART Setup

Create virtual serial port -> creates two devices e.g. /dev/pts/3, /dev/pts/4:

```bash
socat -d -d pty,rawer,echo=0 pty,rawer,echo=0
```

Read / write to serial port from console to test the software:

```bash
# minicom -D <port> -H -b 115200
# E.g. read on one and write on second:
minicom -D /dev/ttys047 -H -b 115200
minicom -D /dev/ttys048 -H -b 115200
```

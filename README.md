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

```shell
# create virtual environment
python3 -m venv venv
# initialize virtual environment
source venv/bin/activate
# install dependencies
python3 -m pip install -r requirements.txt
```

## Configuration

```toml
# config.toml
[auth]
team_nr = "03"
token = "<auth_token>"

[server]
api_address = "<ip_address>:<port>"
rtsp_address = "<ip_address>"

[rtsp]
user = "pren"
password = "<password>"
profile = "<pren_profile_small|pren_profile_med>"

[app]
confidence = 25
recognition_timeout = 60
serial_read = "/dev/ttyAMA0"
serial_write = "/dev/ttyAMA0"
```

## Deployment

```shell
source venv/bin/activate
python3 main.py
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

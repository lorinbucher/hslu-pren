# HSLU PREN Team 03

## Table of Contents

* [Installation](#installation)
* [Configuration](#configuration)
* [Deployment](#deployment)
* [Development](#development)
  * [Code Quality Check](#code-quality-check)

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

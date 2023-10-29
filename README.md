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
python3 -m venv ~/.virtualenvs/hslu-pren
# initialize virtual environment
source ~/.virtualenvs/hslu-pren/bin/activate
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
```

## Deployment

```shell
source ~/.virtualenvs/hslu-pren/bin/activate
python3 main.py
```

## Development

### Code Quality Check

```shell
source ~/.virtualenvs/hslu-pren/bin/activate
mypy .
pylint '**/*.py' --recursive=yes
```

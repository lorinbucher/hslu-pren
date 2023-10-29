# HSLU PREN Team 03

## Table of Contents

* [Installation](#installation)
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

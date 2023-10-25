#!/usr/bin/env bash
# Code Quality Check

# Exit the script if an error occurs
set -euo pipefail

########################################################################################################################
# Configuration
readonly script_dir=$(dirname "$(readlink -f "${BASH_SOURCE:-$0}")")
readonly work_dir="${script_dir}/.."

########################################################################################################################
# Main
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "No virtual environment found"
  exit 1
fi

cd "${work_dir}" || exit 1
mypy .
pylint '**/*.py' --recursive=yes

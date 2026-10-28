#!/usr/bin/env bash

cd "$(dirname -- ${BASH_SOURCE[0]})"

if ! command -v python3 > /dev/null; then
  echo "Python3 unavailable..."
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  echo "Creating python virtual environmet."
  python3 -m venv .venv
fi

source .venv/bin/activate
echo "Running pip install upgrade"
python3 -m pip install -U pip

echo "Pip installing ansible"
python3 -m pip install ansible
deactivate

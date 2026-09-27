#!/usr/bin/env bash

cd "$(dirname -- ${BASH_SOURCE[0]})"

if command -v ansible-playbook > /dev/null; then
  APB='ansible-playbook'
elif [[ -f ./ansible/.venv/bin/ansible-playbook ]]; then
  APB='./ansible/.venv/bin/ansible-playbook'
else
  echo "Couldn't find ansible, attempting to install in python venv"
  sleep 1
  ./ansible/setup-pyvenv.sh
  APB='./ansible/.venv/bin/ansible-playbook'
fi

"$APB" -c local -i "localhost," ansible/setup-ux.yml "$@" && source "$HOME/.bashrc"




#!/usr/bin/env bash
SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

cd "$SCRIPT_DIR" || exit 1

if command -v ansible-playbook > /dev/null; then
  APB='ansible-playbook'
elif [[ -f ./ansible-ux/.venv/bin/ansible-playbook ]]; then
  APB='./ansible-ux/.venv/bin/ansible-playbook'
else
  echo "Couldn't find ansible, attempting to install in python venv"
  sleep 1
  ./ansible/init-venv.sh
  APB='./ansible-ux/.venv/bin/ansible-playbook'
fi

"$APB" -c local -i "localhost," ansible-ux/main.yml "$@" && source "$HOME/.bashrc"




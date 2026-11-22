#!/usr/bin/bash

# shellcheck disable=SC2034
SCRIPT="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT")" && pwd -P)"
PROJECT_DIR="$PWD"
PROJECT_NAME=""
PROJECT_SSH_KEY=""
INSTALL_ROLES=false
INSTALL_COLLECTIONS=false

# Display help message with -h
print_help() {
    cat <<EOF

usage: $SCRIPT

options:
    -h (Print this help text)
    -p [PROJECT_DIR]
    -n [PROJECT_NAME]
    -k [PROJECT_SSH_KEY]
    -R (Install roles from requirements.yml)
    -C (Install collections from requirements.yml)

EOF
}

# Set Options/Arguments
while getopts ':hp:n:k:RC' opt; do
    case "$opt" in
        h) print_help && exit 0 ;;
        p) PROJECT_DIR="$OPTARG" ;;
        n) PROJECT_NAME="$OPTARG" ;;
        k) PROJECT_SSH_KEY="$OPTARG" ;;
        R) INSTALL_ROLES=true ;;
        C) INSTALL_COLLECTIONS=true ;;
        :) printf 'Missing argument -%s\n' "$OPTARG" && exit 1 ;;
        \?) printf 'Invalid argument -%s\n' "$OPTARG" && exit 1 ;;
    esac
done

shift "$(( OPTIND - 1 ))"

make_dirs() {
    mkdir -p "$PROJECT_DIR"/inventory/{host,group}_vars \
        "$PROJECT_DIR"/playbooks/{tasks,files,vars,templates,handlers,vault} \
        "$PROJECT_DIR"/roles \
        "$PROJECT_DIR"/collections \
        "$PROJECT_DIR"/library \
        "$PROJECT_DIR"/module_utils \
        "$PROJECT_DIR"/.secrets
}

make_files() {
    for s in vault become connection; do
        touch "$PROJECT_DIR/.secrets/$s-pass"
        chmod 600 "$PROJECT_DIR/.secrets/$s-pass"
    done

    cat > "$PROJECT_DIR"/ansible.cfg <<EOF
[defaults]
host_key_checking = false
interpreter_python = auto_silent
deprecation_warnings = false
display_ok_hosts = true
display_skipped_hosts = false
display_args_to_stdout = false

forks = 10
remote_user = ansible
editor = vim
private_key_file = .secrets/ansible_key

# ask_vault_pass = false
# vault_password_file = .secrets/vault-pass
# ask_become_pass = false
# become_password_file = .secrets/become-pass
# ask_pass = false
# connection_password_file = .secrets/connection-pass

inventory = ./inventory:~/.ansible/inventory:/usr/share/ansible/inventory
roles_path = ./roles:~/.ansible/roles:/usr/share/ansible/roles
collections_path = ./collections:~/.ansible/collections:/usr/share/ansible/collections
library = ./library:~/.ansible/library:/usr/share/ansible/library
module_utils = ./module_utils:~/.ansible/module_utils:/usr/share/ansible/module_utils
log_path = ansible.log

EOF

    cat > "$PROJECT_DIR"/requirements.yml <<EOF
---
collections:
  - name: ansible.posix
  - name: ansible.netcommon
  - name: ansible.utils
  - name: community.general
  - name: community.crypto
  - name: community.libvirt
  - name: fedora.linux_system_roles
  - name: everpure.flashblade
  - name: everpure.flasharray
  - name: cisco.ios
  - name: cisco.nxos
  - name: arista.eos

roles:
  - name: ansible-lockdown.rhel10_stig
  - name: ansible-lockdown.rhel9_stig
  - name: ansible-lockdown.rhel8_stig
  - name: ansible-lockdown.rhel7_stig
  - name: geerlingguy.apache
  - name: geerlingguy.certbot
  - name: geerlingguy.clamav
  - name: geerlingguy.nginx
  - name: geerlingguy.nfs
  - name: geerlingguy.docker
  - name: geerlingguy.containerd
  - name: geerlingguy.kubernetes
  - name: geerlingguy.gitlab

EOF

    cat > "$PROJECT_DIR"/inventory/hosts.yml <<EOF
---
all:
  hosts:
    localhost:
      ansible_host: 127.0.0.1

EOF
}

# Copy or setup ssh keys for ansible project
setup_ssh_keys() {
    if [[ -n "$PROJECT_SSH_KEY" && -f "$PROJECT_SSH_KEY" ]]; then
        cp -v "$PROJECT_SSH_KEY" "$PROJECT_DIR"/.secrets/ansible_key 
        cp -v "$PROJECT_SSH_KEY".pub "$PROJECT_DIR"/.secrets/ansible_key.pub 
        chmod 600 "$PROJECT_DIR"/.secrets/ansible_key
    else
        ssh-keygen -t rsa -b 4096 -C "Ansible Key - $PROJECT_NAME" -f "$PROJECT_DIR"/.secrets/ansible_key -N '' -q
    fi
    
}

# Install generated requirements.yml from ansible galaxy
install_requirements() {
    if [[ -f "$PROJECT_DIR"/requirements.yml ]]; then
        if [[ "$INSTALL_COLLECTIONS" == true ]]; then
            ansible-galaxy collection install -f -p "$PROJECT_DIR/collections" -r "$PROJECT_DIR/requirements.yml"
        fi

        if [[ "$INSTALL_ROLES" == true ]]; then
            ansible-galaxy role install -f -p "$PROJECT_DIR/roles" -r "$PROJECT_DIR/requirements.yml"
        fi
    fi
}

# Change permissions of secrets
chmod_secrets() {
    chmod 0700 "$PROJECT_DIR"/.secrets
    chmod 0600 "$PROJECT_DIR"/.secrets/*
}

### Main ###

main() {
    make_dirs
    make_files
    setup_ssh_keys
    install_requirements
    chmod_secrets

    exit 0
}

main



#!/usr/bin/env bash

VMPOOL=$1
VMNAME=${2:-}
virt-install --name "$VMNAME" \
    --vcpus  

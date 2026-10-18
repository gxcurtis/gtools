#!/usr/bin/env bash

VM_NAME='virt-machine'
VCPUS=2
MEMORY=4096
DISK_SIZE=120
INSTALL_DISK='installer-disk.img'
BOOT='uefi'
# BOOT='/usr/share/edk2/ovmf/OVMF_CODE.fd' 
OS='linux2024'

while getopts ':o:n:c:m:d:i:b:' opt; do
    case "$opt" in
        o) OS=$OPTARG ;;
        n) VM_NAME="$OPTARG" ;;
        c) VCPUS="$OPTARG" ;;
        m) MEMORY="$OPTARG" ;;
        d) DISK_SIZE="$OPTARG" ;;
        i) INSTALL_DISK=$OPTARG ;;
        b) BOOT="$OPTARG" ;;
        :) printf 'Missing argument -%s' "$OPTARG" || exit 1 ;;
        \?) printf 'Invalid argument -%s' "$OPTARG" || exit 1 ;;
    esac
done

shift $(( OPTIND - 1 ))

VMPOOL=${1:-}
if [[ -z $VMPOOL ]]; then
    printf 'ERROR: VMPOOL not specified.\n'
    exit 1
fi

VMPOOL="${VMPOOL%/}"
virt-install --name "$VM_NAME" \
    --os-variant "$OS" \
    --vcpus "$VCPUS" \
    --memory "$MEMORY" \
    --disk path="$VMPOOL"/"$VM_NAME".qcow2,size="$DISK_SIZE",format=qcow2,bus=virtio,boot.order=1 \
    --disk path="$VMPOOL"/"$INSTALL_DISK",format=raw,bus=virtio,boot.order=2,readonly=on \
    --console pty,target.type=serial \
    --serial pty \
    --graphics spice \
    --boot "$BOOT"


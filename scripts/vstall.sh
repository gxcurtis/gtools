#!/usr/bin/env bash

VMNAME="$1"
CPUS=16
MEM=32768
DISK_SIZE=200

if [[ -z $VMNAME ]]; then
    echo "Set vm name."
    exit 1
fi 

sudo virt-install --osinfo rhel8.9 --name "$VMNAME" \
    --vcpus "$CPUS" --memory "$MEM" --graphics none --serial pty \
    --disk path=/vmcrypt/pool/"${VMNAME}"-base.qcow2,size="$DISK_SIZE",boot_order=1 \
    --disk path=/vmcrypt/pool/ce-install.img,readonly=on,shareable=on,boot_order=2 \
    --boot loader=/usr/share/edk2/ovmf/OVMF_CODE.cc.fd,loader.readonly=yes,loader.type=pflash \
    --check path_in_use=off


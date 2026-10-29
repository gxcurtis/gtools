#!/usr/bin/bash

vm_name=""
snap_name=""
vm_pool="/vmcrypt/pool"
dry_run=false
merge=false
rollback=false

while getopts ':v:s:p:dMR' opt; do
    case "$opt" in
        v) vm_name="$OPTARG" ;;
        s) snap_name="$OPTARG" ;;
        p) vm_pool="$OPTARG" ;;
        d) dry_run=true ;;
        M) merge=true ;;
        R) rollback=true ;;
        :) printf 'Missing argument -%s' "$OPTARG" ;;
        \?) printf 'Invalid argument -%s' "$OPTARG" ;;
    esac
done

shift "$(( OPTIND - 1 ))"

if [[ -z $vm_name ]]; then
    echo "Specify vm name with -v"
    exit 1
fi

if [[ -z $snap_name ]]; then
    echo "Specify snapshot name with -s"
    exit 1
fi

if [[ $merge == "true" && $rollback == "true" ]]; then
    echo "Cannot use merge(-M) and rollback(-R) options together..."
    exit 1
fi

if [[ "$dry_run" == "true" ]]; then
    printf '\nCommand Preview:\n----------------\n'

    if [[ $merge == "true" ]]; then
        cat <<EOF
sudo virsh blockcommit $vm_name vda --pivot OR sudo qemu-img commit -p $vm_pool/${vm_name}.${snap_name}
sudo virsh snapshot-delete $vm_name $snap_name --metadata
sudo rm -i $vm_pool/${vm_name}.${snap_name}

EOF
    elif [[ $rollback == "true" ]]; then
        echo "TODO: implement rollback commands"
    else
        cat <<EOF
sudo virsh snapshot-create-as $vm_name $snap_name \\
    --disk-only --atomic --quiesce \\
    --diskspec vda,snapshot=external,driver=qcow2

EOF
    fi
    exit 0
fi

# Main
if [[ $merge == "true" ]]; then
    if [[ $(virsh domstate "$vm_name") == "shut off" ]]; then
        sudo qemu-img commit -p $vm_pool/${vm_name}.${snap_name}
    else
        sudo virsh blockcommit $vm_name vda --pivot
    fi

    sudo virsh snapshot-delete $vm_name $snap_name --metadata
    sudo rm -i $vm_pool/${vm_name}.${snap_name}

elif [[ $rollback == "true" ]]; then
    echo "TODO: implement rollback commands"
else
    sudo virsh snapshot-create-as $vm_name $snap_name \
        --disk-only --atomic --quiesce \
        --diskspec vda,snapshot=external,driver=qcow2
fi

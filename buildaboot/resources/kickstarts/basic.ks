# Produced by ksbuilder
lang en_US.UTF-8
keyboard --vckeymap=us --xlayouts='us'
timezone Etc/UTC --utc
text
reboot
firstboot --disable
eula --agreed

network --bootproto=dhcp --device=link --activate
firewall --enable --use-system-defaults

rootpw --iscrypted $6$usUN4E78ZA.Fkik.$euyecIiBQChSmOx/SY27dy.4TXSfcgui6Tvvudg8SwPxIRyuOGKZM21tjI.1CA.lqtH8mt.A8eHQdBmlkCwUL/
 
bootloader --location=mbr

user --name=ansible --password=$6$cNic6m3yEZltkr5W$WNextPJuUjmkrIyIDfu0kKNZpyCk3CW4SdydWKXh.fp/m43Y.qxWdJlFq8ukLMXwqFg3VnLphk5faEd796.kd1 --iscrypted --homedir=/home/ansible --shell=/bin/bash --gecos='Ansible Admin' --groups=wheel

%include /tmp/part-include

%pre --interpreter=/usr/bin/bash --log=/tmp/pre-kickstart.log --erroronfail

partfile="/tmp/part-include"
ignore_label=INSTALL

# Sizes in MiB
bootefi_size=600
boot_size=1024

# Min/Max disk size in bytes
MIN_SIZE=0
(( MAX_SIZE = 2199023255552 )) # 2048 G

# Get install disk by label to ignore it
get_install_disk() {
    local device parent
    device="$(readlink -f /dev/disk/by-label/"$ignore_label")" || return 1
    parent="$(lsblk -no PKNAME "$device")" || return 1

    if [[ -n "$parent" ]]; then
        device="$parent"
    else
        device="${device##*/}"
    fi

    printf '%s' "$device" 
}

install_disk="$(get_install_disk)"
filtered_disks=()
smallest_disk=''
smallest_disk_size=0

# Filter for qualified disks
while read -r name size removable; do
    [[ "$install_disk" != "$name" ]] || continue
    ((removable == 0)) || continue
    [[ "$name" =~ ^(vd|sd|nvme) ]] || continue
    (( MIN_SIZE <= size && size <= MAX_SIZE )) || continue

    if (( smallest_disk_size == 0 || size < smallest_disk_size )); then
    # Set initial smallest disk
        smallest_disk="$name"
        smallest_disk_size="$size"
        filtered_disks=("$smallest_disk")
    elif (( smallest_disk_size == size )); then
        filtered_disks+=("$name")
    else
        continue
    fi
done < <(lsblk -ndbo NAME,SIZE,RM)

num_disks="${#filtered_disks[@]}"

if [[ $num_disks -lt 1 ]]; then
    printf 'ERROR: NO DISKS FOUND!\n'
    exit 1
else
  zerombr
  ignoredisk --only-use="${filtered_disks[0]}"
  clearpart --all --initlabel --drives="${filtered_disks[0]}"
  autopart
fi

%end

%packages --ignoremissing
@core
bash-completion
man-db
man-pages
tmux
vim-enhanced

%end

%post --interpreter=/usr/bin/bash --log=/root/post-kickstart.log

echo "Hello World!"

%end


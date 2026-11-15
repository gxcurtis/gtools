# Produced by ksbuilder
lang en_US.UTF-8
keyboard --vckeymap=us --xlayouts='us'
timezone Etc/UTC --utc
timesource --ntp-server=time.nist.gov
text
reboot
firstboot --disable
eula --agreed

network --bootproto=dhcp --device=link --activate --noipv6 --nameserver=9.9.9.9,8.8.8.8,1.1.1.1
firewall --enable --ssh

selinux --enforcing
rootpw --iscrypted $6$eCsf9rrxSUrMRZ17$4ouMViFxKqtOIpMU6Pip2M5gRLdb95eeAS3olXAlFZGqJuvOcULO03ZgwMWDu0oonFc1xhXVwltFkICkIvDkL/
 
bootloader --location=mbr --append="fips=1 audit=1 audit_backlog_limit=8192" --iscrypted --password=grub.pbkdf2.sha512.10000.FE6A21C122B6A4D47DD876D043FD0F47059B8986272900C2ABF89D553F71DE4E3B68A2856CEBA2DA886C9396D8264FB629269817CFAD86A61D148552521D6C65.746C1630E9197545077721323EA4FA06A18073E51772559D5E95C01E385563C5F27110D3E2CBF04ACD87D758238D5934D43D2C09EDD57BF8C181B17F72819ADE # Bootloader superuser: bootadmin

user --name=ansible --password=$6$L2zutGcjQxhMqNAZ$4zqg1HupEMLCBYcliiMaGW5n4tGJlr1uO3t6TF8wRVco6YanBDfI2u3NiZc6gbiFStROts3i3bOTCqschYapR0 --iscrypted --homedir=/home/ansible --shell=/bin/bash --gecos='Ansible Admin' --groups=wheel

%include /tmp/part-include

%pre --interpreter=/usr/bin/bash --log=/tmp/pre-kickstart.log --erroronfail

partfile="/tmp/part-include"
ignore_label=INSTALL
vgname=os

# Sizes in MiB
bootefi_size=600
boot_size=1024

# Min/Max disk size in bytes
(( MIN_SIZE = 53242494976 )) # 49 G
(( MAX_SIZE = 2199023255552 )) # 2048 G

lv_root=("/" "root" "xfs" 20480)
lv_home=("/home" "home" "xfs" 10240)
lv_scratch=("/scratch" "scratch" "xfs" 2048)
lv_tmp=("/tmp" "tmp" "xfs" 2048)
lv_var=("/var" "var" "xfs" 2048)
lv_vartmp=("/var/tmp" "vartmp" "xfs" 2048)
lv_varlog=("/var/log" "varlog" "xfs" 2048)
lv_journal=("/var/log/journal" "journal" "xfs" 2048)
lv_audit=("/var/log/audit" "audit" "xfs" 2048)
lv_swap=("swap" "swap" "swap" 4096)

# Array of logical volume arrays
LOGVOLS=(lv_root  lv_home  lv_scratch  lv_tmp  lv_var  lv_vartmp  lv_varlog  lv_journal  lv_audit  lv_swap)

# Output logical volumes defined in LOGVOLS
emit_lvm() {
  # Grow LVM storage up to 80% storage capacity
  local disk_size="$1"
  local percent=80
  local percent_size=$(( disk_size / (1024 * 1024) * percent / 100 ))
  local baseline_size=$(( MIN_SIZE / (1024 * 1024) ))
  local scale_factor=$(( percent_size * 4 / baseline_size ))
printf '%s\n' "volgroup $vgname pv.01"

for logvol in "${LOGVOLS[@]}"; do
  local -n lv="$logvol"

  # Scale up logical volume by calculated factor (lv[3] = size)
  (( scale_factor > 4 )) && (( lv[3] = (lv[3] / 4) * scale_factor ))

  printf 'logvol %s --vgname=%s --name=%s --fstype=%s --size=%s\n' \
    "${lv[0]}" \
    "${vgname}" \
    "${lv[1]}" \
    "${lv[2]}" \
    "${lv[3]}"
done
}

# Output single disk partition scheme
emit_single() {
    test -n "$1" || exit 1
    local os_disk="$1"

    cat << EOF
ignoredisk --only-use=$os_disk
clearpart --all --initlabel --drives=$os_disk
zerombr

part /boot/efi --fstype=efi --size=$bootefi_size --ondisk=$os_disk
part /boot --fstype=xfs --size=$boot_size --ondisk=$os_disk
part pv.01 --fstype=lvmpv --size=1 --grow --ondisk=$os_disk --encrypted --passphrase=install

EOF
}

# Output double disk raid 1 partition scheme
emit_raid1() {
    test -n "$1" || exit 1
    test -n "$2" || exit 2
    local os_disk1="$1"
    local os_disk2="$2"

    cat << EOF
ignoredisk --only-use=$os_disk1,$os_disk2
clearpart --all --initlabel --drives=$os_disk1,$os_disk2
zerombr

part raid.01 --size=$bootefi_size --ondisk=$os_disk1
part raid.02 --size=$bootefi_size --ondisk=$os_disk2
raid /boot/efi --device=md0 --level=1 --fstype=efi raid.01 raid.02

part raid.11 --size=$boot_size --ondisk=$os_disk1
part raid.12 --size=$boot_size --ondisk=$os_disk2
raid /boot --device=md1 --level=1 --fstype=xfs raid.11 raid.12

part raid.21 --size=1 --grow --ondisk=$os_disk1
part raid.22 --size=1 --grow --ondisk=$os_disk2
raid pv.01 --device=md2 --level=1 --fstype=lvmpv raid.21 raid.22 --encrypted --passphrase=install

EOF
}

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
elif [[ $num_disks -eq 1 ]]; then
    emit_single "${filtered_disks[0]}" > "$partfile"
else
    emit_raid1 "${filtered_disks[0]}" "${filtered_disks[1]}" > "$partfile"
fi

emit_lvm "$smallest_disk_size" >> "$partfile"

%end

%packages --ignoremissing
@^server-product-environment
@core
@headless-management
@security-tools
bash-completion
curl
info
man-db
man-pages
openssl
rsync
tmux
vim-enhanced

%end

%addon org_fedora_oscap
  content-type = scap-security-guide
  profile = xccdf_org.ssgproject.content_profile_stig
%end

%post --interpreter=/usr/bin/bash --log=/root/post-kickstart.log

systemctl enable serial-getty@ttyS0.service

# Reconfigure grub bootloader user from default 'root'
sed -i \
    -e 's/set superusers="root"/set superusers="bootadmin"/' \
    -e 's/password_pbkdf2 root /password_pbkdf2 bootadmin /' \
    /etc/grub.d/01_users

if [ -d /sys/firmware/efi ]; then
    grub2-mkconfig -o /etc/grub2-efi.cfg
else
    grub2-mkconfig -o /etc/grub2.cfg
fi

# Configure firewalld default zone
target_zone=drop
services=$(firewall-offline-cmd --list-services)
ports=$(firewall-offline-cmd --list-ports)

for service in $services; do
    firewall-offline-cmd --zone="$target_zone" --add-service="$service"
done

for port in $ports; do
  firewall-offline-cmd --zone="$target_zone" --add-port="$port"
done

firewall-offline-cmd --set-default-zone="$target_zone"

%end


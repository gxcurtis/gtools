#!/usr/bin/env bash

stamp="$(date '+%b%d_%H%M%S')"
ksfile="${1:-${stamp}.ks}"
partfile=/tmp/partition-scheme
root_pwhash='{{ }}'
ansible_pwhash='{{ }}'
grub_pwhash='{{ }}'


emit_locale() {
    local tz="${1:-Etc/UTC}"

    cat >> "$ksfile" << EOF
lang en_US.UTF-8
keyboard --vckeymap=us --xlayouts='us'
timezone=$tz

EOF
}

emit_standard() {
    cat >> "$ksfile" << EOF
text
reboot
firstboot --disable
eula --agreed

EOF
}

emit_security() {
    cat >> "$ksfile" << EOF
firewall --enable --ssh
selinux --enforcing
rootpw --iscrypted $root_pwhash
bootloader --iscrypted --password=$grub_pwhash

EOF
}

emit_network() {
    cat >> "$ksfile" << EOF
# network --bootproto={{ }} --device={{ }} --hostname={{ }} --activate --gateway={{ }} --ip={{ }} --mtu={{ }} --nameserver={{ }} --netmask={{ }} --ipv4-dns-search={{ }} 

EOF
}

emit_repos() {
    cat >> "$ksfile" << EOF
# repo --name={{ }} --baseurl={{ }} --mirrorlist={{ }} --install
# repo --name={{ }} --baseurl={{ }} --mirrorlist={{ }} --install
# repo --name={{ }} --baseurl={{ }} --mirrorlist={{ }} --install
# repo --name={{ }} --baseurl={{ }} --mirrorlist={{ }} --install
    
EOF
}

emit_packages() {
    cat >> "$ksfile" << EOF
%packages
@core
curl
tmux
rsync
openssl
tcpdump
nmap-ncat
vim-enhanced
openscap-scanner
scap-security-guide
policycoreutils-python-utils
ShellCheck
yum-utils
nfs-utils
httpd
%end

EOF
}

cat > "$ksfile" << EOF
# Anaconda Kickstart

EOF

emit_locale
emit_standard
emit_security
emit_network
emit_repos

cat >> "$ksfile" << EOF
%include $partfile

%end

%pre --interpreter=/usr/bin/bash
EOF

sed '1,3d' bashpart >> "$ksfile"

cat >> "$ksfile" << EOF
%end

EOF

emit_packages

cat >> "$ksfile" << EOF
%post

%end

EOF

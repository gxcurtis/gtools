text
reboot
firstboot --disable

lang en_US.UTF-8
keyboard us
timezone UTC --utc

network --bootproto=dhcp --device=link --activate
firewall --enabled --service=ssh

selinux --enforcing
rootpw --lock
user --name=admin --groups=wheel --password='$6$I9ZuW36S/847tpiu$DkfKcRF6L.S996Zwzh8wbggNNfdDA4OEMg3uCYLC72JgSts/vDD3EN2PtYiwLrrZr0v7IyYoxALvyTMma5bWC.' --iscrypted

zerombr
clearpart --all --initlabel
autopart --type=lvm
%include /tmp/ignoredisk.ks

%pre --erroronfail --log=/tmp/ks-pre.log
installdisk=$(lsblk -ndo PKNAME /dev/disk/by-label/INSTALL)
if [ -z "$installdisk" ]; then
  echo "No INSTALL disk found!"
  exit 1
fi
echo "ignoredisk --drives=$installdisk" > /tmp/ignoredisk.ks
%end

%packages
@core
openssh-server
vim-enhanced
bind-utils
nmap-ncat
curl
wget
tmux
%end

%post
systemctl enable sshd
systemctl enable serial-getty@ttyS0.service
%end

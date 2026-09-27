eula --agreed
firstboot --disabled
lang en_US.UTF-8
keyboard --vckeymap=us --xlayouts='us'
timezone America/Phoenix --utc

bootloader --location=none --append="rd.live.image rd.live.ram=1 loglevel=4 console=tty0 console=ttyS0,115200n8"

network --bootproto=dhcp --hostname=fedora-rescue --device=link --onboot=yes --activate

url --url="https://download.fedoraproject.org/pub/fedora/linux/releases/44/Everything/x86_64/os/"

ignoredisk --only-use=sda
clearpart --all --initlabel --drives=sda

part /boot/efi --fstype=efi --size=512 --ondisk=sda
part / --fstype=ext4 --size=32768 --ondisk=sda --label=FEDORA

firewall --disabled

selinux --disabled

rootpw --lock

user --name=gino --groups=wheel --shell=/bin/bash --iscrypted --password=$6$miOUn4uWA7.VOxkv$oYl.Kv8ihJM.qaOJ30H4SAoLPNWpq.iT90KH8QqDtMjNIeaInGUIkeQCEw2XugQaWvQJ92EC2iEsYSwUX0yy/1

shutdown

%packages
@core
kernel
kernel-modules-extra
dracut-live
dracut-config-generic
grub2-tools
grub2-tools-extra
grub2-efi-x64
grub2-efi-x64-modules
grub2-efi-x64-cdboot
grub2-pc
grub2-pc-modules
shim-x64
man-db
man-pages
info
tldr
less
bat
jq

dnf-utils
bind-utils
nfs-utils
usbutils
pciutils
binutils
cloud-utils-growpart
policycoreutils-python-utils
acl
lsof
strace
ltrace
file
procps-ng
psmisc
htop
libvirt-client
qemu-img
dmidecode
createrepo_c
openssl
sudo

lm_sensors
memtest86+
stress-ng
rasdaemon

mdadm
lvm2
cryptsetup
xfsprogs
e2fsprogs
parted
ddrescue
smartmontools
iotop
gdisk
testdisk
partclone

xz
zip
gzip
zstd
bzip2
tar

NetworkManager
openssh-server
httpd

gawk
sed
grep
bash
findutils
ShellCheck
vim-enhanced
vim-ale
awesome-vim-colorschemes

tmux
screen
minicom
pv

openssh-clients
rsync
curl
wget
aria2
git
tcpdump
nmap-ncat
nload
iperf3
iproute
ethtool
net-tools
arp-scan

nmap
clamav
clamav-freshclam
openscap-scanner
openscap-utils
scap-security-guide
wireshark-cli
rkhunter
chkrootkit
sleuthkit
masscan
aircrack-ng
hashcat
hydra
binwalk
foremost
perl-Image-ExifTool

python3
python3-requests
python3-scrapy
python3-beautifulsoup4
python3-selenium
python3-pyyaml
python3-jinja2
python3-ansible-lint
python3-mypy
ruff
ansible
yamllint

gcc
gcc-c++
clang
clang-tools-extra
cppcheck
gdb
make
cmake
ninja-build

golang
staticcheck

glibc-devel
libstdc++-devel
pkgconf-pkg-config
zlib-devel
bzip2-devel
xz-devel
openssl-devel
libcurl-devel
libssh-devel
ncurses-devel
readline-devel
sqlite-devel
libxml2-devel
libyaml-devel
systemd-devel
libcap-devel
libseccomp-devel
elfutils-libelf-devel
libffi-devel
python3-devel

%end

%post --erroronfail
set -e

: > /etc/fstab

echo "%wheel ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/wheelies
chmod 0440 /etc/sudoers.d/wheelies
visudo -cf /etc/sudoers.d/wheelies

systemctl set-default multi-user.target
systemctl enable NetworkManager
systemctl enable sshd

cat > /home/gino/.vimrc << 'EOF'
" Core syntax
colorscheme industry
set encoding=utf-8
set number
set numberwidth=1
set timeout
set timeoutlen=500

" Navigation keybindings
inoremap jh <Esc>
nnoremap j h
nnoremap k j
nnoremap l k
nnoremap ; l

vnoremap j h
vnoremap k j
vnoremap l k
vnoremap ; l

nnoremap <M-;> ;
vnoremap <M-;> ;
onoremap <M-;> ;

nnoremap <Esc>k <C-f>
nnoremap <Esc>l <C-b>

vnoremap <Esc>k <C-f>
vnoremap <Esc>l <C-b>

nnoremap <C-w>j <C-w>h
nnoremap <C-w>k <C-w>j
nnoremap <C-w>l <C-w>k
nnoremap <C-w>; <C-w>l

" Defaults
set tabstop=4
set shiftwidth=4
set softtabstop=4
set expandtab
set autoindent

" Python
augroup ft_python
  autocmd!
  autocmd FileType python setlocal expandtab tabstop=4 softtabstop=4 shiftwidth=4
augroup END

" C & C++
augroup ft_c
  autocmd!
  autocmd FileType c,cpp setlocal expandtab tabstop=4 softtabstop=4 shiftwidth=4
  autocmd FileType c,cpp setlocal cindent
augroup END

" Bash, YAML, HTML, CSS 
augroup ft_others
  autocmd!
  autocmd FileType sh,bash,yaml,html,css setlocal expandtab tabstop=2 softtabstop=2 shiftwidth=2
augroup END

EOF

chown gino:gino /home/gino/.vimrc
chmod 0440 /home/gino/.vimrc

cat >> /home/gino/.bashrc << 'EOF'

# Prompt
PS1='\[\033[1;37m\][\[\033[1;36m\]\u\[\033[1;37m\]@\[\033[1;35m\]\h\[\033[1;37m\]:\[\033[1;33m\]\W\[\033[1;37m\]]\$ \[\033[0m\]'

EOF

chown gino:gino /home/gino/.bashrc
chmod 0440 /home/gino/.bashrc


%end

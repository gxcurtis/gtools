# Migrate OS to New Storage Media

Migrate an OS from one drive to another.

__Two methods:__
    - `dd` command
    - `rsync` command + manual formatting

## dd Method

From seperate boot method and both disks not being used run the following:

```sh
$ sudo dd if=/dev/sdX of=/dev/sdY bs=16M conv=fsync status=progress
```

Creates an exact byte for byte clone of source disk. This is okay in situations when you want to keep the exact same disk format. This becomes less straight forward when destination needs to be formatted differently.

## Rsync Method

__Technologies:__
    - UEFI Firmware
    - GPT Partition Table
    - Grub2 Bootloader
    - RHEL-Like OS (dracut)
    - parted (fdisk/gdisk work)
    - mdadm (If used)
    - Luks (If used)
    - LVM (If used)
    
__Commands:__
    - `lsblk`
    - `blkid`
    - `parted`
    - `mdadm`
    - `cryptsetup`
    - `pvcreate`
    - `vgcreate`
    - `lvcreate`
    - `mkfs.vfat`
    - `mkfs.xfs or mkfs.ext4`
    - `mount`
    - `rsync`
    - `chroot`
    - `grub2-mkconfig`
    - `grubby`
    - `dracut`
    - `umount`
    - `reboot`
    
__Configuration Files:__
    - `/etc/fstab`
    - `/etc/mdadm.conf`
    - `/etc/crypttab`
    - `/etc/default/grub`
    - `/boot/loader/entries/*`
    - `/boot/grub2/grubenv`
    - `/boot/efi/EFI/<distro>/*`

__Kernel Commandline Args:__
    - `rd.md.uuid=<ARRAY-UUID>` (mdadm)
    - `rd.luks.uuid=<LUKS-UUID>`
    - `rd.lvm.lv=<VG/LV>`
    - `root=<DEV-PATH-TO-ROOT>`
    - `resume=<DEV-PATH-TO-SWAP>`
    - `boot=UUID=<BOOT-UUID>` (FIPS)
    - ``

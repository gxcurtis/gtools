#!/usr/bin/env bash
set -euo pipefail

SCRIPT="$0"
ESP_LABEL='BOOTME'
DATA_LABEL='INSTALL'
DEV="${1:-}"
ESP_MOUNTPOINT="/mnt/ESP"
DATA_MOUNTPOINT="/mnt/DATA"
EFI_BOOT_DIR="$ESP_MOUNTPOINT/EFI/BOOT"
GRUB_DIR="$DATA_MOUNTPOINT/boot/grub2"
RESOURCE_DIR="$DATA_MOUNTPOINT/resources/"
DISTRO_DIRS=(
  rhel/{7..10}
  rocky/{8..10}
  centos/{8..10}
  fedora
)

usage() {
  echo
  echo "Usage: sudo $SCRIPT <device> (e.g. /dev/sdX /dev/loopX)"
  exit 1
}

dependencies_installed() {
  PKG_DEPS=(
    gdisk
    parted
    dosfstools
    grub2-pc
    grub2-efi-x64
    grub2-tools
    grub2-tools-extra
    grub2-pc-modules
    grub2-efi-x64-modules
  )

  local missing_deps=()
  for pkg in "${PKG_DEPS[@]}"; do
    if ! rpm -q --quiet "$pkg"; then
      echo "Missing dependency: $pkg"
      missing_deps+=("$pkg")
    fi
  done
  
  if [[ "${#missing_deps[@]}" -gt 0 ]]; then
    while true; do
      read -r -p "Would you like to install missing dependencies? (y/n): " answer
      case "$answer" in
        [Yy]) 
          echo "Installing... "
          sleep 1
          dnf install -y "${missing_deps[@]}" && return 0
            ;;
        [Nn]) 
          return 1
          ;;
        *)  
          echo "Invalid answer $answer"
          ;;
      esac
    done
    return 0
  fi
}

partition_device() {
  local device="$1"

  if mountpoint -q "$ESP_MOUNTPOINT"; then
    umount -f "$ESP_MOUNTPOINT"
  fi
  if mountpoint -q "$DATA_MOUNTPOINT"; then
    umount -f "$DATA_MOUNTPOINT"
  fi

  wipefs -a "$device"
  sgdisk --zap-all "$device"
  dd if=/dev/zero of="$device" bs=1M count=16 conv=fsync
  parted --script --align optimal "$device" \
    mklabel gpt \
    mkpart BIOS 1MiB 3MiB \
    set 1 bios_grub on \
    mkpart UEFI fat32 3MiB 515MiB \
    set 2 esp on \
    mkpart DATA ext4 515MiB 100% \
    print

  if [[ "$device" =~ [0-9]$ ]]; then
    local part2="${device}p2"
    local part3="${device}p3"
  else
    local part2="${device}2"
    local part3="${device}3"
  fi

  mkfs.vfat -F32 -n "$ESP_LABEL" "$part2"
  mkfs.ext4 -F -L "$DATA_LABEL" "$part3"
}

stage_files_directories() {
  mkdir -p "$ESP_MOUNTPOINT" "$DATA_MOUNTPOINT"

  mount -L "$ESP_LABEL" "$ESP_MOUNTPOINT" 
  mount -L "$DATA_LABEL" "$DATA_MOUNTPOINT"

  mkdir -p "$EFI_BOOT_DIR"
  mkdir -p "$GRUB_DIR" "${DISTRO_DIRS[@]/#/$DATA_MOUNTPOINT/}"

  if [[ -d "$DATA_MOUNTPOINT/lost+found" ]]; then
    rmdir "$DATA_MOUNTPOINT/lost+found"
  fi

  cp -a /usr/lib/grub/x86_64-efi "$GRUB_DIR/"
  cp -a /usr/lib/grub/i386-pc "$GRUB_DIR/"
  cp -a resources "$DATA_MOUNTPOINT/"

  chmod -R a+rX "$DATA_MOUNTPOINT/"
}

setup_grub_bios() {
  grub2-install \
    --target=i386-pc \
    --boot-directory="$DATA_MOUNTPOINT/boot" \
    "$DEV"
}

setup_grub_efi() {
  local embedded_cfg="$EFI_BOOT_DIR/embedded.cfg"
  local grub_cfg="$RESOURCE_DIR/grubmenus/grub.cfg"
  
  if ! mountpoint -q "$ESP_MOUNTPOINT"; then
    echo
    echo "Error: $ESP_MOUNTPOINT not mounted."
    exit 2
  fi

  if ! mountpoint -q "$DATA_MOUNTPOINT"; then
    echo
    echo "Error: $ESP_MOUNTPOINT not mounted."
    exit 2
  fi

  cat <<- EOF > "$embedded_cfg"
search --no-floppy --label $DATA_LABEL --set=root
set prefix=(\$root)/boot/grub2
configfile /boot/grub2/grub.cfg
EOF

  local grub_modules="
  part_gpt
  part_msdos
  fat
  ext2
  xfs
  search
  search_label
  normal
  configfile
  "

  grub2-mkstandalone \
    -O x86_64-efi \
    -o "$EFI_BOOT_DIR/BOOTX64.EFI" \
    --modules="$grub_modules" \
    "boot/grub/grub.cfg=$embedded_cfg"

  cp "$grub_cfg" "$GRUB_DIR"
}

cleanup() {
  while true; do
    read -r -p "Would you like to cleanup and unmount partitions? (y/n): " answer
    case "$answer" in
      [Yy])
        echo "Flushing memory to disk before unmounting..."
        sync
        umount "$ESP_MOUNTPOINT"
        umount "$DATA_MOUNTPOINT"
        
        rmdir "$ESP_MOUNTPOINT"
        rmdir "$DATA_MOUNTPOINT"

        sleep 1
        echo "Cleanup complete."
        break
        ;;
      [Nn])
        echo "Skipping cleanup."
        break
        ;;
      *)
        echo "Invalid response: $answer"
        ;;
    esac
  done
}

# MAIN #
if [[ -z "$DEV" ]]; then
  echo "Missing <device> argument."
  usage
elif [[ ! -b "$DEV" ]]; then
  echo "Invalid block device $DEV"
  usage
elif [[ "$EUID" -ne 0 ]]; then
  echo "Must run as root (sudo)."
  usage
elif ! dependencies_installed; then
  echo "Package dependencies not installed. Aborting..."
  exit 1
else
  echo
  echo "ATTENTION: Script will WIPE the following device:"

  echo
  lsblk -o name,size,type,label -d "$DEV"

  echo
  read -r -p "If you still wish to continue enter ERASE in all caps: " answer
  if [[ "$answer" != ERASE ]]; then
    echo "Aborting..."
    exit 1
  else
    sleep 2
  fi

  partition_device "$DEV"
  stage_files_directories
  setup_grub_bios
  setup_grub_efi
  echo

  printf "Boot device setup.\n\n"
  lsblk -o name,size,type,mountpoint,label "$DEV"
  echo
  cleanup
  sleep 1 && printf "BYE!\n" && sleep 1
fi


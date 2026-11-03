#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from xml.etree.ElementTree as ET

def build_parser():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="mode", required=True, help="Snapshot mode")

    kvm_parser = subparsers.add_parser("kvm", help="KVM virsh mode")
    qemu_parser = subparsers.add_parser("qemu", help="QEMU image mode")
    lvm_parser = subparsers.add_parser("lvm", help="LVM logical volume mode")
#    zfs_parser = subparsers.add_parser("zfs", help="ZFS file system mode")
#    btrfs_parser = subparsers.add_parser("btrfs", help="BTRFS file system mode")

    kvm_parser.add_argument("vm", help="Virtual Machine Name/Domain")
    kvm_parser.add_argument("--disk-only", action="store_true", default=True, help="Disk only snapshot")
    kvm_parser.add_argument("", help="")

    qemu_parser.add_argument("qcow2", help="Path to qcow2 file")

    lvm_parser.add_argument("lv", help="Path to logical volume block device")


def run(*args, **kwargs):
    if sys.version_info >= (3,8):
        kwargs["capture_output"] = True
        kwargs["text"] = True
    else:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE
        kwargs["universal_newlines"] = True

    return subprocess.run("sudo", *args, **kwargs)


def virsh_xml():
    pass

def virsh_state():
    pass

def snapshot():
    pass

def revert():
    pass

def merge():
    pass



#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import Element


# Subprocess wrapper
def run(capture=True, *args, **kwargs):
    if capture:
        if sys.version_info >= (3,8):
            kwargs["capture_output"] = True
            kwargs["text"] = True
        else:
            kwargs["stdout"] = subprocess.PIPE
            kwargs["stderr"] = subprocess.PIPE
            kwargs["universal_newlines"] = True

    kwargs["check"] = True

    return subprocess.run(["sudo", *args], **kwargs)


class Disk:
    def __init__(self, disk_element: Element):
        self.name = disk_element.find("target").get("dev")
        self.type = disk_element.get("type")
        self.format = disk_element.find("driver").get("type")
        self.bus = disk_element.find("target").get("bus")
        
        if self.type == "file":
            self.source = disk_element.find("source").get("file")
        elif self.type == "block":
            self.source = disk_element.find("source").get("dev")
        else:
            self.source = None


class VM:
    def __init__(self, name):
        self.name = name
        self.disks = self.get_disks()

    def virsh_xml(self):
        result = run("virsh", "dumpxml", self.name)

        return ET.fromstring(result.stdout)

    def get_disks(self):
        xml = self.virsh_xml()

        disks = xml.findall("devices/disk")
        
        return [Disk(disk) for disk in disks]

    def get_state(self):
        result = run("virsh", "domstate", self.vm)

        return result.stdout.strip()


def build_subparsers(snapshot_type: str, subparsers: argparse._SubParsersAction) -> list[argparse.ArgumentParser]:
    next_parser = subparsers.add_parser(snapshot_type)
    next_subparser = next_parser.add_subparsers(dest="snapshot_action")
    
    actions = ["create", "commit", "revert"]

    return [next_subparser.add_parser(action) for action in actions]

def build_parser():
    parser = argparse.ArgumentParser()

    common = argparse.ArgumentParser(add_help=False)
    

    subparsers = parser.add_subparsers(dest="snapshot_command")
    create = subparsers.add_parser("create")
    commit = subparsers.add_parser("commit")
    revert = subparsers.add_parser("revert")

    # Build subparsers
    kvm_create, kvm_commit, kvm_revert = build_subparsers("kvm", subparsers)
    qemu_create, qemu_commit, qemu_revert = build_subparsers("qemu", subparsers)
    lvm_create, lvm_commit, lvm_revert = build_subparsers("lvm", subparsers)

    # KVM Create Args
    kvm_create.add_argument("vm_name", type=VM, help="VM name")
    kvm_create.add_argument("-n", "--overlay-name", default="overlay", help="Set snapshot overlay name")
    kvm_create.add_argument("-d", "--virtual-disk", default="vda", help="Set disk to target")
    kvm_create.add_argument("-q", "--quiesce", action="store_true", help="Use qemu guest agent to freeze filesystem before snapshot")
    kvm_create.add_argument("-i", "--internal", action="store_true", help="Specify internal snapshot type")
    kvm_create.add_argument("-a", "--atomic", action="store_true", help="All or nothing snapshot success or failure. No partial.")

    # KVM Commit Args
    kvm_commit.add_argument("vm_name", type=VM, help="VM name")
    kvm_commit.add_argument()


    # KVM Revert Args
    
    # Unique arguments to QEMU parser
    qemu_parser.add_argument("qcow2_file", type=Path, help="Path to qcow2 file")
    qemu_parser.add_argument("-n", "--overlay-name", default="overlay", help="Set snapshot overlay name")
    qemu_parser.add_argument("-i", "--internal", action="store_true", help="Specify internal snapshot type")

    # Unique arguments to LVM parser
    lvm_parser.add_argument("lv_path", type=Path, help="LVM logical volume device path")
    lvm_parser.add_argument("-n", "--snapshot-name", default="snapshot", help="Set snapshot name")
    lvm_parser.add_argument("-s", "--size", help="Set size (G) for CoW space")
    lvm_parser.add_argument("-T", "--thinpool", action="store_true", help="Specify thin-provisioned snapshot type")
    
    return parser

def snapshot():
    pass

def revert():
    pass

def merge():
    pass


### MAIN ###

def main():
    parser = build_parser()
    args = parser.parse_args()

    args

if __name__ == "__main__":
    sys.exit(main())

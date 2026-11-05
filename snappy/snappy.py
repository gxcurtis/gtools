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

class LogicalVolume:
    def __init__(self, device_path):
        self.device_path = device_path
        self.name = None
        self.volume_group = None
        self.attrs = []
        self.size = None
        self.set_lvs_info()

    def set_lvs_info(self):
        result = run("lvs", "--noheadings", self.device_path)
        
        fields = result.stdout.split()

        self.name = fields[0]
        self.volume_group = fields[1]
        self.attrs = [atrr for attr in fields[2] if attr != '-']
        self.size = fields[3]

def snapshot_type(snapshot_target: str) -> VM | LogicalVolume:
    try:
        target = VM(snapshot_target)
    except subprocess.CalledProcessError as e:
        target = LogicalVolume(snapshot)
            

def build_parser():
    parser = argparse.ArgumentParser()

    # Build subparsers
    parser.add_argument("snapshot_targets", type=snapshot_type(), nargs="+", help="Specify virtual machines or logical volumes to snapshot")
    parser.add_argument("-n", "--snapshot-name", default="snapshot", help="Specify snapshot or overlay name")
    parser.add_argument("-d", "--virtual-disk", default="vda", help="Specify virtual disk to target, only applicable to VMs (default: vda)")
    parser.add_argument("-s", "--volume-size", default="20G", help="Specify volume size to provision snapshot, only applicable to LVM (default: 20G)")
    
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("-C", "--commit", action="store_true", help="COMMIT and remove snapshot changes to source target")
    action_group.add_argument("-R", "--revert", action="store_true", help="REVERT and remove snapshot changes to source target")

    return parser

class Snapshot:

    @staticmethod
    def create(args: argparse.Namespace):
        for target in args.snapshot_targets:
            if isinstance(target, VM):
                disk_specs = []
                for disk in target.disks:
                    disk_specs.append("--diskspec")
                    if disk.name == args.virtual_disk:
                        disk_specs.append(f"{args.virtual_disk},snapshot=external,driver=qcow2")
                    else:
                        disk_specs.append(f"{disk.name},snapshot=no")

                run("virsh", "snapshot-create-as", target.name, args.snapshot_name, "--disk-only", *disk_specs)
            
            elif isinstance(target, LogicalVolume):
                pass

    @staticmethod
    def commit(args: argparse.Namespace):
        pass

    @staticmethod
    def revert(args: argparse.Namespace):
        pass


### MAIN ###

def main():
    parser = build_parser()
    args = parser.parse_args()

    args

if __name__ == "__main__":
    sys.exit(main())

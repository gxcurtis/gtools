#!/usr/bin/env python3
import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element


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


class Snapshot:
    def __init__(self, name):
        self.name = name
        self.create_commands = []
        self.commit_commands = []
        self.revert_commands = []

    def _add_command(self, *args, commit=False, revert=False):
        if commit:
           self.commit_commands.append(args) 
        elif revert:
           self.revert_commands.append(args) 
        else:
           self.create_commands.append(args) 

    def run(self, *args, capture=True, **kwargs):
        if capture:
            if sys.version_info >= (3,8):
                kwargs["capture_output"] = True
                kwargs["text"] = True
            else:
                kwargs["stdout"] = subprocess.PIPE
                kwargs["stderr"] = subprocess.PIPE
                kwargs["universal_newlines"] = True

        return subprocess.run(["sudo", *args], check=True, **kwargs)


    def create(self, args: argparse.Namespace):
        for cmd in self.create_commands():
            self.run(*cmd, capture=False)

    def commit(self):
        for cmd in self.commit_commands():
            self.run(*cmd, capture=False)

    def revert(self):
        for cmd in self.revert_commands():
            self.run(*cmd, capture=False)


class LVSnapshot(Snapshot):
    def __init__(self, device_path, snapshot_size):
        self.device_path = device_path
        self.snapshot_size = snapshot_size
        self.logical_volume = None
        self.volume_group = None
        self.lv_attrs = []
        self.lv_size = None
        self.set_lvs_info()
        
    def set_lvs_info(self):
        result = self.run("lvs", "--noheadings", self.device_path)
        
        fields = result.stdout.split()

        self.logical_volume = fields[0]
        self.volume_group = fields[1]
        self.lv_attrs = [attr for attr in fields[2] if attr != '-']
        self.lv_size = fields[3]


class VMSnapshot(Snapshot):
    def __init__(self, domain):
        self.domain = domain
        self.disks = self.get_disks()

    def virsh_xml(self):
        result = self.run("virsh", "dumpxml", self.domain)

        return ET.fromstring(result.stdout)

    def get_disks(self):
        xml = self.virsh_xml()

        disks = xml.findall("devices/disk")
        
        return [Disk(disk) for disk in disks]

    def get_state(self):
        result = self.run("virsh", "domstate", self.vm)

        return result.stdout.strip()

    def _add_vmsnapshot_commands(self):
        snapshot_command = ["virsh", "snapshot-create-as", self.domain, self.name, "--disk-only", "--atomic", "--diskspec", f"{},snapshot=external"]

def snapshot_type(snapshot_target: str) -> VMSnapshot | LVSnapshot:
    try:
        target = VMSnapshot(snapshot_target)
    except subprocess.CalledProcessError:
        target = LVSnapshot(snapshot_target)

    return target
            

def build_parser():
    parser = argparse.ArgumentParser()

    # Build subparsers
    parser.add_argument("snapshot_targets", type=snapshot_type, nargs="+", help="Specify virtual machines or logical volumes to snapshot")
    parser.add_argument("-n", "--snapshot-name", default="snapshot", help="Specify snapshot or overlay name")
    parser.add_argument("-d", "--virtual-disk", default="vda", help="Specify virtual disk to target, only applicable to VMs (default: vda)")
    parser.add_argument("-s", "--volume-size", default="20G", help="Specify volume size to provision snapshot, only applicable to LVM (default: 20G)")
    
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("-C", "--commit", action="store_true", help="COMMIT and remove snapshot changes to source target")
    action_group.add_argument("-R", "--revert", action="store_true", help="REVERT and remove snapshot changes to source target")

    return parser

##########
## MAIN ##
##########

def main():
    parser = build_parser()
    args = parser.parse_args()

    for snapshot_target in args.snapshot_targets:
        if args.revert:
            snapshot_target.revert()
        elif args.commit:
            snapshot_target.commit()
        else:
            snapshot_target.create(args)

if __name__ == "__main__":
    sys.exit(main())

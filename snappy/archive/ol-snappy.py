#!/usr/bin/env python3
import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import Element


class Disk:
    def __init__(self, disk_element: Element):
        self.name = disk_element.find("target").get("dev")
        self.type = disk_element.get("type")
        self.format = disk_element.find("driver").get("type")
        self.bus = disk_element.find("target").get("bus")
        
        if self.type == "file":
            self.source = Path(disk_element.find("source").get("file"))
        elif self.type == "block":
            self.source = Path(disk_element.find("source").get("dev"))
        else:
            self.source = None


class Snapshot:
    def __init__(self, name="snapshot"):
        self.name = name

    def run(self, *args, capture=True, **kwargs):
        if capture:
            if sys.version_info >= (3,8):
                kwargs["capture_output"] = True
                kwargs["text"] = True
            else:
                kwargs["stdout"] = subprocess.PIPE
                kwargs["stderr"] = subprocess.PIPE
                kwargs["universal_newlines"] = True

        try:
            return subprocess.run(["sudo", *args], check=True, **kwargs)
        except subprocess.CalledProcessError as e:
            sys.exit(e.stderr)

    def set_snapshot_name(self, snapshot_name):
        self.name = snapshot_name

    def create(self, virtual_disk: str, volume_size: str):
        if isinstance(self, VMSnapshot):
            snapshot_command = ["virsh", "snapshot-create-as", self.domain, self.name, "--disk-only", "--atomic", "--diskspec", f"{virtual_disk},snapshot=external"]
            
            for disk in self.disks:
                if disk.name != virtual_disk:
                    snapshot_command.append("--diskspec")
                    snapshot_command.append(f"{disk.name},snapshot=no")

            self.run(*snapshot_command, capture=False)

        elif isinstance(self, LVSnapshot):
            pass

        else:
            pass

    def commit(self, virtual_disk: str, volume_size: str):
        
        if isinstance(self, VMSnapshot):
            self.run("virsh", "blockcommit", self.domain, virtual_disk, "--pivot", "--shallow", capture=False)
            
            snapshot_disk = self.get_snapshot_disk(virtual_disk)
            if snapshot_disk.source.suffix == f".{self.name}":
                snapshot_disk.source.unlink(missing_ok=True)

        elif isinstance(self, LVSnapshot):
            pass

        else:
            pass

    def revert(self, virtual_disk: str, volume_size: str):

        if isinstance(self, VMSnapshot):
            disk_source = self.get_snapshot_disk(virtual_disk).source

            updated_root = self.update_disk_source(virtual_disk, str(disk_source.with_suffix(".qcow2"))
  
            ET.ElementTree(updated_root).write(
                f"/tmp/{self.domain}-reverted.xml",
                encoding="utf-8",
                xml_declaration=True
            )

            self.run("virsh", "destroy", self.domain)
            self.run("virsh", "define", f"/tmp/{self.domain}-reverted.xml", capture=False)

            if disk_path.suffix == f".{self.name}":
                disk_path.unlink(missing_ok=True)    

        elif isinstance(self, LVSnapshot):
            pass

        else:
            pass

class LVSnapshot(Snapshot):
    def __init__(self, device_path, snapshot_name="snapshot"):
        super().__init__(snapshot_name)
        self.device_path = device_path
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
    def __init__(self, domain, snapshot_name="snapshot"):
        super().__init__(snapshot_name)
        self.domain = domain
        self.disks = self.get_disks()
        self.xml_root = self.virsh_xml()

    def virsh_xml(self):
        result = self.run("virsh", "dumpxml", self.domain)

        return ET.fromstring(result.stdout)

    def get_state(self):
        result = self.run("virsh", "domstate", self.vm)

        return result.stdout.strip()

    def get_disks(self):
        xml = self.virsh_xml()

        disks = xml.findall("devices/disk")
        
        return [Disk(disk) for disk in disks]

    def get_snapshot_disk(self, virtual_disk: str):
        for disk in self.disks:
            if disk.name == virtual_disk:
                return disk
        
    def update_disk_source(self, virtual_disk: str, disk_path: str):
        root = self.virsh_xml()

        for disk in root.findall("./devices/disk"):
            disk_target = disk.find("target")

            if disk_target is not None and disk_target.get("dev") == virtual_disk:
                disk_source = disk_target.find("source")

                if disk_source is not None:
                    source.set("file", disk_path)
                    return root


def snapshot_type(snapshot_target: str) -> VMSnapshot | LVSnapshot:
    try:
        target = VMSnapshot(snapshot_target)
    except subprocess.CalledProcessError as e:
        try:
            target = LVSnapshot(snapshot_target)
        except subprocess.CalledProcessError as e:
            raise

    return target
            

def build_parser():
    parser = argparse.ArgumentParser()

    # Build subparsers
    parser.add_argument("snapshot_targets", type=snapshot_type, nargs="+", help="Specify virtual machines or logical volumes to snapshot")
    parser.add_argument("-n", "--snapshot-name", default="snapshot", help="Specify snapshot or overlay name (default: snapshot)")
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
        snapshot_target.set_snapshot_name(args.snapshot_name)

        if args.revert:
            snapshot_target.revert(args.virtual_disk, args.volume_size)
        elif args.commit:
            snapshot_target.commit(args.virtual_disk, args.volume_size)
        else:
            snapshot_target.create(args.virtual_disk, args.volume_size)

if __name__ == "__main__":
    sys.exit(main())

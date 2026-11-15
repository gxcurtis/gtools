import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from pathlib import Path

class VirtualMachine:
    def __init__(self, domain: str):
        self.domain = domain
        self.backing_chain()

    def dumpxml(self, xpath=None):
        cmd = ["virsh", "dumpxml", self.domain]

        if xpath:
            cmd.extend("--xpath", xpath)

        result = run(*cmd).stdout

        return result.stdout

    def get_disk_xml(self, disk):
        xml_disks = ET.fromstring(self.dumpxml(xpath='devices/disk'))
        pass

    def update_backing_chain(self, disk_xml: Element):
        if not (backing_store := disk_xml.find("backingStore")):
            pass

       
        

            
            
        
    def create_snapshot(self, snapshot_name, disk_only=True, atomic=True):
        cmd = [ 
            "virsh",
            "snapshot-create-as",
            self.domain,
            snapshot_name 
        ]    
        
        if disk_only:
            cmd.append("--disk-only")

        if atomic:
            cmd.append("--atomic")

        return run(*cmd, capture=False)

    def commit_snapshot(self, snapshot_name, pivot=True)
        cmd = [
            "virsh",
            "blockcommit",
            self.domain,
        ]

def build_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("snapshot_cmd", choices=["create", "commit", "revert"], help="Snapshot command")

    parser.add_argument("-s", "--snapshot-name", default="snappy", help="Specify snapshot name (default: snappy)")

    parser.add_argument("vms", nargs="+", type=VirtualMachine, help="QEMU/KVM Virtual Machines")

    return parser

def run(*args, capture=True, check=True **kwargs):
    if capture:
        if sys.version_info >= (3,8):
            kwargs["capture_output"] = True
            kwargs["text"] = True
        else:
            kwargs["stdout"] = subprocess.PIPE
            kwargs["stderr"] = subprocess.PIPE
            kwargs["universal_newlines"] = True

    try:
        return subprocess.run(["sudo", *args], check=check, **kwargs)
    except subprocess.CalledProcessError as e:
        sys.exit(e.stderr)

##########
## MAIN ##
##########

def main():
    parser = build_parser()
    args = parser.parse_args()

if __name__ == "__main__":
   sys.exit(main()) 

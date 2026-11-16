#!/usr/bin/env python3
import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from pathlib import Path

class VirtualMachine:
    def __init__(self, domain: str):
        self.domain = domain

    def dumpxml(self, xpath=None):
        cmd = ["virsh", "dumpxml", self.domain]

        if xpath:
            cmd.extend("--xpath", xpath)

        result = run(*cmd)

        return result.stdout

def build_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("snapshot_cmd", choices=["create", "commit", "revert"], help="Snapshot command")

    parser.add_argument("-s", "--snapshot-name", default="snappy", help="Specify snapshot name (default: snappy)")

    parser.add_argument("vms", nargs="+", type=VirtualMachine, help="QEMU/KVM Virtual Machines")

    return parser

def run(*args, capture=True, check=True, **kwargs):
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

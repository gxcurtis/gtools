#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from xml.etree.ElementTree as ET

def build_parser():
    parser = argparse.add_argument("vmname", help="Virtual machine name")
    parser = argparse.add_argument("-o", "--overlay-name", default="snapshot-overlay", help="Snapshot overlay name")
    parser = argparse.add_argument("-p", "--vmpool", default=os.cwd(), help="Path to VM pool")
    parser = argparse.add_argument("-d", "--detach-disks", nargs="+", help="Detach disks from VM")
    parser = argparse.add_argument("-a", "--attach-disks", nargs="+", help="Attach disks to VM")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-M", "--merge-overlay", action="store_true", help="Merge overlay back into chain")
    group.add_argument("-R", "--rollback", action="store_true", help="Rollback to previous state and discard changes")

    return parser

def run(*args, **kwargs):
    if sys.version_info >= (3,8):
        kwargs["capture_output"] = True
        kwargs["text"] = True
    else:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE
        kwargs["universal_newlines"] = True

    return subprocess.run("sudo", *args, **kwargs)

def vm_state(vm):
    result = run("virsh", "domstate", vm)

    return result.stdout.strip()

def get_backing_file(vm, disk="vda"):
    result = run("virsh", "domblkinfo", vm, "--details")



def make_overlay(vm, overlay, disk="vda"):
    create_cmd = [
        "virsh",
        "snapshot-create-as",
        vm,
        overlay,
        "--atomic",
        "--disk-only",
        "--diskspec",
        f"{disk},snapshot=external,driver=qcow2"
    ]

    if "running" in vm_state():
        create_cmd.append("--quiesce")

    run(create_cmd)

def merge_back(vm, overlay):
    state = vm_state()

    if "shut off" in state:
        merge_cmd = [
            "qemu-img",
            "commit",
        ]
    elif "running" in state:

    else:
        raise RuntimeError("VM State is not running or shut off")

    run("virsh")

def roll_back():
    pass

def tach_disk():
    pass

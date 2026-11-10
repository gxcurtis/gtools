import argparse
import sys
from pathlib import Path
from .virtual_machine import VirtualMachine
from .logical_volume import LogicalVolume

def build_parser():
    parser = argparse.ArgumentParser()

    # Top level args
    parser.add_argument("-n", "--snapshot-name", default="snappy", help="Specify snapshot or overlay name (default: snappy)")
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("-C", "--commit", action="store_true", help="COMMIT and remove snapshot changes to source target")
    action_group.add_argument("-R", "--revert", action="store_true", help="REVERT and remove snapshot changes to source target")

    # Second level subcommands
    subparsers = parser.add_subparsers(dest="snapshot_type", required=True)
    virt_parser = subparsers.add_parser("virt")
    lvm_parser = subparsers.add_parser("lvm")

    # Third level virtual machine args
    virt_parser.add_argument("vm", type=VirtualMachine, nargs="+", dest="snapshot_targets", help="Name of virtual machines to snapshot")

    return parser

##########
## MAIN ##
##########

def main():
    parser = build_parser()
    args = parser.parse_args()

    for target in args.snapshot_targets():
        target.snapshot.name = args.snapshot_name

        # Commit execution branch
        if args.commit:
            if isinstance(target, VirtualMachine):
                target.snapshot.commit_commands = (
                    ("virsh", "blockcommit", target.domain, target.overlay_path, "--pivot", "--shallow"),
                    ("virsh", "snapshot-list", target.domain),
                    ("virsh", "domblklist", target.domain)
                )
            elif isinstance(target, LogicalVolume):
                pass
            else:
                pass

            target.snapshot.commit(target)

        # Revert execution branch
        elif args.revert:
            if isinstance(target, VirtualMachine):
                target.write_reverted_xml(f"/tmp/{target.domain}-reverted.xml")
                target.snapshot.revert_commands = (
                    ("virsh", "destroy", target.domain),
                    ("virsh", "define", str(target.tmp_xml_path),
                    ("virsh", "snapshot-list", target.domain),
                    ("virsh", "domblklist", target.domain)
            elif isinstance(target, LogicalVolume):
                pass
            else:
                pass

            target.snapshot.revert(target)

        # Create execution branch
        else:
            if isinstance(target, VirtualMachine):
                target.set_create_commands = (
                    ("virsh", "snapshot-create-as", target.domain, target.snapshot.name, "--disk-only", "--atomic"),
                    ("virsh", "snapshot-list", target.domain),
                    ("virsh", "domblklist", target.domain)
                )
            elif isinstance(target, LogicalVolume):
                pass
            else:
                pass

            target.snapshot.create(target)


if __name__ == "__main__":
   sys.exit(main()) 

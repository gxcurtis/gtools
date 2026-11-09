import argparse
import sys
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
            # Set instance specific attributes 
            if isinstance(target, VirtualMachine):
                #target.set_disk()
                pass
            elif isinstance(target, LogicalVolume):
                #target.set_size()
                pass
            else:
                pass

            target.set_commit_commands()
            target.snapshot.commit(target)

        # Revert execution branch
        elif args.revert:
            # Set instance specific attributes 
            if isinstance(target, VirtualMachine):
                pass
            elif isinstance(target, LogicalVolume):
                pass
            else:
                pass

            target.set_revert_commands()
            target.snapshot.revert(target)

        # Create execution branch
        else:
            # Set instance specific attributes 
            if isinstance(target, VirtualMachine):
                pass
            elif isinstance(target, LogicalVolume):
                pass
            else:
                pass

            target.set_create_commands(
                ("virsh", "snapshot-create-as", self.domain, self.snapshot.name, "--disk-only", "--atomic")
            )

            target.snapshot.create(target)


if __name__ == "__main__":
   sys.exit(main()) 

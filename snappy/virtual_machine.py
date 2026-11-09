import xml.etree.ElementTree as ET

from .snapshot_manager import SnapshotManager
from .utils import run

class VirtualMachine:
    def __init__(self, domain: str):
        self.domain = domain
        self.snapshot = SnapshotManager()

    def dumpxml(self, inactive=True):
        cmd_args = ["virsh", "dumpxml", self.domain]
        if inactive:
            cmd_args.append("--inactive")

        result = run(*cmd_args).stdout

        return result.stdout

    def set_create_commands(self):
        commands = []

        self.snapshot.create_commands = commands

    def set_commit_commands(self):
        commands = []

        self.snapshot.commit_commands = commands

    def set_revert_commands(self):
        commands = []
        
        self.snapshot.revert_commands = commands
        

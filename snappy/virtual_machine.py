import xml.etree.ElementTree as ET

from .snapshot_manager import SnapshotManager
from .utils import run

class VirtualMachine:
    def __init__(self, domain: str):
        self.domain = domain
        self.snapshot = SnapshotManager()
        self.overlay_path = None

    def dumpxml(self, inactive=True):
        cmd_args = ["virsh", "dumpxml", self.domain]
        if inactive:
            cmd_args.append("--inactive")

        result = run(*cmd_args).stdout

        return result.stdout

    def write_reverted_xml(self):
        pass

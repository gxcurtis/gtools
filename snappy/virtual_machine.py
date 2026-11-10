import subprocess
import xml.etree.ElementTree as ET

# Command function
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

class VirtualMachine:
    def __init__(self, domain: str):
        self.domain = domain

    def dumpxml(self, inactive=False, xpath=None):
        cmd = ["virsh", "dumpxml", self.domain]

        if inactive:
            cmd.append("--inactive")

        if xpath:
            cmd.extend("--xpath", xpath)

        result = run(*cmd).stdout

        return result.stdout

    def get_backing(self, element: ET.Element, results=[]):
        source = element.find("source")
        file = source.get("file")

        results.insert(file)

        backing_store = element.find("backingStore")
        if backing_store:
            backing_source = backing_store.find("source")

            if backing_source:
                backing_file = backing_file.get("file")

        if backing_file is None:
            return results

        return self.get_backing(backin)

            
    def get_backing_chain(self, target_disk):
        xml_disks = ET.fromstring(self.dumpxml(xpath='devices/disk'))
        
        for disk in xml_disks:
            source_file = disk.find("source").get("file")
            target_dev = disk.find("target").get("dev")

            if target_dev == target_disk:
                return source_file

        return None
            
        
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


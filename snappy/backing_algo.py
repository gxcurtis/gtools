#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from snappy import VirtualMachine

def print_xml(el: Element):
    if not isinstance(el, Element):
        print("Expecting xml Element instance. Got", type(el))
        return
    ET.indent(el)
    ET.ElementTree(el).write(sys.stdout, encoding="unicode")
    print()

def update_backing(disk: Element):
    source = disk.find("backingStore").find("source")
    if (backingfile := source.get("file")) is not None:

    
vm = VirtualMachine("vm")
vm_xml = vm.dumpxml()

#print(vm_xml)

root = ET.fromstring(vm_xml)

#print(type(root))

disks = root.findall('devices/disk')

for disk in disks:
    print_xml(disk)
    print()
    source = disk.find("backingStore").find("source")
    if (backingfile := source.get("file")) is not None: 
        disk.find("source").set("file", backingfile)
        disk.remove(disk.find("backingStore"))
        print_xml(disk)
    else:
        print("backingStore not found")





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

def update_backing(node: Element):
    source = node.find("source")
    backing_store = node.find("backingStore")

    if backing_store is None or len(backing_store) == 0:
        return node

    backing_source = backing_store.find("source")
    backing_file = backing_source.get("file")

    child_node = backing_store.find("backingStore")
   
    source.set("file", backing_file)
    node.remove(backing_store)

    if child_node is None or len(child_node) == 0:
        node.append(Element("backingStore"))
    else:
        node.append(child_node)

    return node

vm = VirtualMachine("vm")
vm_xml = vm.dumpxml()

#print(vm_xml)

root = ET.fromstring(vm_xml)

#print(type(root))

disks = root.findall('devices/disk')

for disk in disks:
    print_xml(disk)
    print()
    update_backing(disk)
    print_xml(disk)





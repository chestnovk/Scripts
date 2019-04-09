#!/usr/bin/python3

import xml.etree.ElementTree as ET

# Need to add the following:
"""
<qemu:commandline>
    <qemu:arg value='-initrd'/>
    <qemu:arg value='/root/kchestnov/mounts/vz-iso-7.0.8-514/images/pxeboot/initrd.img'/>
    <qemu:arg value='-append'/>
    <qemu:arg value='inst.stage2=hd:LABEL=vz-iso-7.0.8-514 ui sdevice=eth0 ip=172.16.56.135 netmask=255.255.254.0 ks=http://172.16.56.80/ks/compute_kickstart.cfg netmask=255.255.254.0 vamn= uiip= hostname=anikolayev_storage_1 va_register= ui_register= token='/>
    <qemu:arg value='-kernel'/>
    <qemu:arg value='/root/kchestnov/mounts/vz-iso-7.0.8-514/images/pxeboot/vmlinuz'/>
    <qemu:arg value='-d'/>
    <qemu:arg value='guest_errors,unimp'/>
  </qemu:commandline>
"""

label = "vz-iso-7.0.8-514"
ksdevice = "eth0"
ip = "172.16.56.200"
netmask = "255.255.252.0"
ks = "http://172.16.56.80/ks/compute_kickstart.cfg" 
hostname = "test"
initrd = "/root/kchestnov/mounts/vz-iso-7.0.8-514/images/pxeboot/initrd.img"
append = "inst.stage2=hd:LABEL={} ksdevice={} ip={} netmask={} ks={} vamn= uiip= hostname={} va_register= ui_register= token=".format(label, ksdevice, ip, netmask, ks, hostname)
kernel = "/root/kchestnov/mounts/vz-iso-7.0.8-514/images/pxeboot/vmlinuz"

qemu_ns = {'qemu': 'http://libvirt.org/schemas/domain/qemu/1.0'}

# Create a new object with corresponding tag
list = []
xml_initrd = ET.Element("{http://libvirt.org/schemas/domain/qemu/1.0}arg")
xml_initrd.tag = "{'value': '-initrd'}"

xml_initrd_value = ET.Element("{http://libvirt.org/schemas/domain/qemu/1.0}arg")
xml_initrd_value.tag = "{'value': '{}'}".format(initrd)

xml_kernel = ET.Element("{http://libvirt.org/schemas/domain/qemu/1.0}arg")
xml_kernel.tag = "{'value': '-kernel'}"

xml_kernel_value = ET.Element("{http://libvirt.org/schemas/domain/qemu/1.0}arg")
xml_kernel_value.tag = "{'value': '{}'}".format(kernel)

xml_append = ET.Element("{http://libvirt.org/schemas/domain/qemu/1.0}arg")
xml_append.tag = "{'value': '-append'}"

xml_append_value = ET.Element("{http://libvirt.org/schemas/domain/qemu/1.0}arg")
xml_kernel_value.tag = "{'value': '{}'}".format(append)



print(kernel)
print(initrd)
print(append)

tree = ET.parse('domainxml')
root = tree.getroot()

print(root)


for child in root:
    print(child.tag, child.attrib)

for cmdline in root.findall('qemu:commandline', qemu_ns):
    for options in cmdline.findall():
        print(options)

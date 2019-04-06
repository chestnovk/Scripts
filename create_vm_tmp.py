#!/usr/bin/python3

import os
import re
import sys
import subprocess

class VzVmBaseConfig:

    def __init__(self):

        # Basic settings
        self.vm_iso_path = "vz-7.0.9.iso"
        self.kickstart = "https://172.16.56.80/ks/example.cfg"



        self.root_dir = "/home/kchestnov/create_vm"
        self.mount_dir = self.root_dir + "/mounts"
        self.vm_config_dir = self.root_dir + "/vms"
        
        # Not sure if I want to put it here
        self.vms = []
        
class VzVmConfig:

    def __init__(self, VzVmBaseConfig, iso):

        self.name = "test_vm_number"

        # Management containers
        self.includes_va = "False"
        self.va_ip = ""
        self.includes_storage_ui = "False"
        self.storage_ui_ip = ""

        # Network settings
        # Public net
        self.public_ip = ""
        self.public_mask = "255.255.252.0"
        self.public_gw = "172.16.56.1"
        self.public_dns = "10.30.0.27"
        
        # Private net
        self.private_ip = "192.168.100.2"
        self.private_mask = "255.255.255.0"

        # VNC settings
        self.vnc_mode = "auto"
        self.vnc_passwd = "vnc_nopasswd"

        # Domainxml configuration options
        # -kernel if iso.is_vmlinuz() -> iso.get_vmlinuz()
        # -initrd if iso.is_initrd()  -> iso.get_initrd()
        # -commandline

class iso:

    def __init__(self, iso_path, mount_dir):

        if not os.path.isfile(iso_path):
            sys.exit("ERROR. Please input correct path for iso, current: {}".format(vm_iso))
        if not os.path.isdir(mount_dir):
            os.mkdir(mount_dir)

        self.iso_path = iso_path
        self.mount_dir = os.path.join(mount_dir, os.path.splitext(os.path.basename(iso_path))[0])
        self.vmlinuz = "images/pxeboot/vmlinuz"
        self.initrd = "imagex/pxeboot/initrd.img"

    def is_mounted(self):
        pass

    def is_dir_created(self):
        if os.path.isdir(self.mount_dir):
            return True

    def is_dir_empty(self):
        if os.path.isdir(self.mount_dir) and not os.listdir(self.mount_dir):
            return True

    def is_vmlinuz(self):
        if os.path.isfile(os.path.join(self.mount_dir,self.vmlinuz)):
            return True

    def is_initrd(self):
        if os.path.isfile(os.path.join(self.mount_dir,self.initrd)):
            return True
    # Fixme
    def get_vmlinuz(self):
        return os.path.isfile(os.path.join(self.mount_dir,self.vmlinuz)) 
    # Fixme
    def get_initrd(self):
        return os.path.isfile(os.path.join(self.mount_dir,self.initrd)) 

    def create_mount_point(self):
        os.mkdir(self.mount_dir)

    def mount(self):
        try:
            subprocess.run(["sudo", "mount", "-o", "loop", self.iso_path, self.mount_dir], check=True)
        except:
            sys.exit("Cannot mount the {} to the {}".format(self.iso_path, self.mount_dir))

    def umount(self):
        try:
            subprocess.run(["sudo", "umount", self.mount_dir], check=True)
        except:
            sys.exit("Cannot mount the {} to the {}".format(self.iso_path, self.mount_dir))



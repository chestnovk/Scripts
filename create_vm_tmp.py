#!/usr/bin/python3

import os
import re
import sys
import subprocess

class VzVmBaseConfig:

    def __init__(self):

        # Basic settings
        self.vm_iso_path = "/home/kchestnov/ISO/CentOS-7-x86_64-Minimal-1810.iso"
        self.kickstart = "https://172.16.56.80/ks/example.cfg"

        self.public_mask = "255.255.252.0"
        self.public_gw = "172.16.56.1"
        self.public_dns = "10.30.0.27"


        self.root_dir = "/home/kchestnov/create_vm"
        self.mount_dir = self.root_dir + "/mounts"
        self.vm_config_dir = self.root_dir + "/vms"
        
        # Not sure if I want to put it here
        self.vms = []
        
class VzVmConfig:

    def __init__(self, VzVmBaseConfig, 
            iso,
            name,
            public_ip,
            private_ip="",
            includes_va=False,
            va_register=False,
            va_ip="",
            includes_storage_ui=False,
            storage_ui_ip="",
            storage_ui_register=False,
            storage_ui_token=""
            ):

        # Define name
        self.name = name

        # Management containers
        if includes_va:
            self.includes_va = includes_va
            self.va_ip = va_ip
        elif register:
            self.va_ip = va_ip

        if includes_storage_ui:
            self.includes_storage_ui = includes_storage_ui
            self.storage_ui_ip = storage_ui_ip
        elif storage_ui_register:
            self.storage_ui_ip = storage_ui_ip
            self.token = storage_ui_token

        # Network settings
        self.ks_device = "eth0"
        self.ks = VzVmBaseConfig.kickstart

        # Public net
        self.public_ip = public_ip

        # To make sure that all VM will get the same 
        # Network settings I obtain the parameters 
        # below from base config
        self.public_mask = VzVmBaseConfig.public_mask
        self.public_gw = VzVmBaseConfig.public_gw
        self.public_dns = VzVmBaseConfig.public_dns
        
        # Private net
        self.private_ip = private_ip
        self.private_mask = "255.255.255.0"

        # VNC settings
        self.vnc_mode = "auto"
        self.vnc_passwd = "vnc_nopasswd"

        # Description for IP
        self.description = "extip:[{} {} {}]".format(self.public_ip, 
                self.va_ip, self.storage_ui_ip)

        # libvirt specific options
        self.domainxml = self.name

        # Maybe this is not worth thing to do.
        # And I can avoid this check later
        self.iso_path = iso.iso_path

        if iso.is_vmlinuz():
            self.vmlinuz = iso.get_vzlinuz()
        if iso.is_initrd():
            self.initrd = iso.get_initrd()

        self.commandline ="inst.stage2=hd:LABEL={} \
                hostname={} \
                ks_device={} \
                public_ip={} \
                public_mask={} \
                public_gw={} \
                public_dns={} \
                ks={} \
                includes_va={} \
                va_ip={} \
                includes_storage_ui={} \
                storage_ui_ip={} \
                private_ip={} \
                private_mask={} \
                ".format(self.hostname, 
                        self.ks_device, 
                        self.public_ip, 
                        self.public_mask, 
                        self.public_gw, 
                        self.dns, 
                        self.ks, 
                        self.includes_va, 
                        self.va_ip, 
                        self.includes_storage_ui, 
                        self.storage_ui_ip, 
                        self.private_ip,
                        self.private_mask)
    def create(self):
        # Create the VM
        subprocess.run(["prlctl", "create", self.name,
                        "--vmtype", "vm",
                        "--distribution", "vzlinux7"], check=True)
        # Add some description
        subprocess.run(["prlctl", "set", self.name, 
                        "--description", self.description,], check=True)
        # Disable filtering
        subprocess.run(["prlctl", "set", self.name, 
                        "--device-set", "net0",
                        "--ipfilter", "no",
                        "--macfilter", "no",
                        "--preventpromisc", "no"], check=True)
        # Create private net
        subprocess.run(["prlsrvctl", "net", "add",
                        self.private_net], check=True)

        # Add nic to the private net
        subprocess.run(["prlctl", "set", self.name,
                        "--device-add", "net",
                        "--network", self.private_net,
                        "", ""], check=True)
        # Add VNC config
        subprocess.run(["prlctl", "set", self.name, ], check=True)

        # Attach cdrom
        subprocess.run(["prlctl", "set", self.name, 
                        "--device-set", "cdrom0",
                        "--connect",
                        "--image", self.iso_path], check=True)

        # Enable support of  nested virt
        subprocess.run(["prlctl", "set", self.name, 
                        "--nested_virt", "on"], check=True)

    def add_kernel_options(self):

        # TO DO:
        # Modify domainxml
        pass

class iso:

    def __init__(self, iso_path, mount_dir):

        if not os.path.isfile(iso_path):
            sys.exit("ERROR. Please input correct path for iso, \
                    current: {}".format(vm_iso))
        if not os.path.isdir(mount_dir):
            os.mkdir(mount_dir)

        self.iso_path = iso_path
        self.mount_dir = os.path.join(mount_dir, 
                os.path.splitext(os.path.basename(iso_path))[0])
        self.vmlinuz = "images/pxeboot/vmlinuz"
        self.initrd = "images/pxeboot/initrd.img"

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

    def get_vmlinuz(self):
        return os.path.join(self.mount_dir,self.vmlinuz) 

    def get_initrd(self):
        return os.path.join(self.mount_dir,self.initrd)

    def create_mount_point(self):
        os.mkdir(self.mount_dir)

    def mount(self):
        try:
            subprocess.run(["sudo", "mount", "-o", "loop", 
                self.iso_path, self.mount_dir], check=True)
        except:
            sys.exit("Cannot mount the {} to the {}".format(self.iso_path,
                self.mount_dir))

    def umount(self):
        try:
            subprocess.run(["sudo", "umount", self.mount_dir], check=True)
        except:
            sys.exit("Cannot mount the {} to the {}".format(self.iso_path,
                self.mount_dir))


# Some kind of "main" is required here. Will add later.



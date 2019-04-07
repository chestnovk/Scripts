#!/usr/bin/python3

import os
import sys
import subprocess


class VzVmBaseConfig:

    def __init__(self, cluster_name):

        # Basic settings
        #self.vm_iso_path = "/home/kchestnov/ISO/CentOS-7-x86_64-Minimal-1810.iso"
        self.vm_iso_path = "/home/kchestnov/create_vm/CentOS-7-x86_64-NetInstall-1810.iso"
        self.kickstart = "https://172.16.56.80/ks/example.cfg"

        self.public_mask = "255.255.252.0"
        self.public_gw = "172.16.56.1"
        self.public_dns = "10.30.0.27"

        self.root_dir = "/home/kchestnov/create_vm"
        self.mount_dir = self.root_dir + "/mounts"
        self.vm_config_dir = self.root_dir + "/vms"

        # Not sure if I want to put it here
        self.cluster_name = cluster_name
        self.vms = []


class VzVmConfig:

    def __init__(
            self,
            VzVmBaseConfig,
            iso,
            name,
            public_ip,
            private_ip="",
            includes_va=False,
            va_register=False,
            va_ip="",
            includes_storage_ui=False,
            storage_ui_register=False,
            storage_ui_ip="",
            storage_ui_token=""
            ):

        # Define name
        self.name = VzVmBaseConfig.cluster_name + "_" + name
        self.hostname = "do-you-really-need-a-hostname"
        self.ips = ""

        # Kickstart location
        self.ks_device = "eth0"
        self.ks = VzVmBaseConfig.kickstart

        # Management containers
        self.includes_va = includes_va
        self.va_register = va_register
        self.includes_storage_ui = includes_storage_ui
        self.storage_ui_register = storage_ui_register
        self.storage_ui_token = storage_ui_token
        self.va_ip = va_ip
        self.storage_ui_ip = storage_ui_ip
        self.storage_ui_token = storage_ui_token

        # Public net
        self.public_ip = public_ip

        # To make sure that all VM will get the same
        # Network settings I obtain the parameters
        # below from base config
        self.public_mask = VzVmBaseConfig.public_mask
        self.public_gw = VzVmBaseConfig.public_gw
        self.public_dns = VzVmBaseConfig.public_dns

        # Private net only when needed. Default False
        self.private_ip = private_ip
        self.private_mask = "255.255.255.0"
        if self.private_ip:
            self.private_net = "pn_for_" + VzVmBaseConfig.cluster_name

        # VNC settings
        self.vnc_mode = "auto"
        self.vnc_passwd = "--vnc-nopasswd"

        # Description for IP
        self.ips = self.ips + self.public_ip

        # Add IP to description if needed
        if self.includes_va:
            self.ips = self.ips + " " + self.va_ip
        elif self.va_register:
            self.ips = self.ips + " " + self.va_ip

        if self.includes_storage_ui:
            self.ips = self.ips + " " + self.storage_ui_ip
        elif self.storage_ui_register:
            self.ips = self.ips + " " + self.storage_ui_ip

        self.description = "extip:[{}]".format(self.ips)

        # libvirt specific options
        self.domainxml = self.name

        # Maybe this is not worth thing to do.
        # And I can avoid this check later
        self.iso_path = iso.iso_path
        self.vmlinuz = iso.get_vmlinuz()
        self.initrd = iso.get_initrd()

        self.commandline = ("inst.stage2=hd:LABEL={} "
                            "hostname={} "
                            "ks_device={} "
                            "public_ip={} "
                            "public_mask={} "
                            "public_gw={} "
                            "public_dns={} "
                            "ks={} "
                            "includes_va={} "
                            "va_ip={} "
                            "includes_storage_ui={} "
                            "storage_ui_ip={} "
                            "private_ip={} "
                            "private_mask={}"
                            ).format(
                                    iso.name,
                                    self.hostname,
                                    self.ks_device,
                                    self.public_ip,
                                    self.public_mask,
                                    self.public_gw,
                                    self.public_dns,
                                    self.ks,
                                    self.includes_va,
                                    self.va_ip,
                                    self.includes_storage_ui,
                                    self.storage_ui_ip,
                                    self.private_ip,
                                    self.private_mask
                                    )

    def create(self):
        # Create the VM
        subprocess.call([
                        "prlctl", "create", self.name,
                        "--vmtype", "vm",
                        "--distribution", "vzlinux7"
                        ], stdout=False)
        # Add some description
        subprocess.call([
                        "prlctl", "set", self.name,
                        "--description", self.description
                        ], stdout=False)
        # Disable filtering
        subprocess.call([
                        "prlctl", "set", self.name,
                        "--device-set", "net0",
                        "--ipfilter", "no",
                        "--macfilter", "no",
                        "--preventpromisc", "no"
                        ], stdout=False)

        # Add VNC config
        subprocess.call([
                        "prlctl", "set", self.name,
                        "--vnc-mode", self.vnc_mode,
                        self.vnc_passwd
                        ], stdout=False)

        # Attach cdrom
        subprocess.call([
                        "prlctl", "set", self.name,
                        "--device-set", "cdrom0",
                        "--connect",
                        "--image", self.iso_path
                        ], stdout=False)

        # Enable support of  nested virt
        subprocess.call([
                        "prlctl", "set", self.name,
                        "--nested-virt", "on"
                        ], stdout=False)

    def set_private_net(self):
        # Create private net
        subprocess.call([
                        "prlsrvctl", "net", "add",
                        self.private_net
                        ], stdout=False)

        # Add nic to the private net
        subprocess.call([
                        "prlctl", "set", self.name,
                        "--device-add", "net",
                        "--network", self.private_net
                        ], stdout=False)

    def start_with_cmdline(self):
        # Obtain params from domainxml
        # Need to find a way to redirect the output
        # to a variable/file so we can restore it 
        # later
        subprocess.call([
                        "virsh","dumpxml",self.domainxml
                        ], stdout=False)
        # TO DO:
        # redirect output
        # Modify domainxml
        # start VM with defined params wiht 
        # virsh start self.name
        pass
    
    def start(self):
        # Simple start by using prlctl
        subprocess.call([
                        "prlctl", "start", self.name
                        ], stdout=False)


class iso:

    def __init__(self, iso_path, mount_dir):

        if not os.path.isfile(iso_path):
            sys.exit("ERROR. Please input correct path for iso "
                    "current: {}".format(iso_path))
        if not os.path.isdir(mount_dir):
            os.mkdir(mount_dir)

        self.name = os.path.splitext(os.path.basename(iso_path))[0]

        self.iso_path = iso_path
        self.mount_dir = os.path.join(
                mount_dir,
                self.name
                )
        self.vmlinuz = os.path.join(self.mount_dir, "images/pxeboot/vmlinuz")
        self.initrd = os.path.join(self.mount_dir, "images/pxeboot/initrd.img")

        if not os.path.isdir(self.mount_dir):
            os.mkdir(self.mount_dir)

    def get_vmlinuz(self):
        # Get initrd.img and vzlinuz
        if not os.path.isfile(self.vmlinuz):
            self.mount()
            return self.vmlinuz
        else:
            return self.vmlinuz

    def get_initrd(self):
        if not os.path.isfile(self.initrd):
            self.mount(self)
            return self.initrd
        else:
            return self.initrd

    def mount(self):
        try:
            subprocess.call([
                            "sudo", "mount", "-o", "loop",
                            self.iso_path, self.mount_dir
                            ], stdout=False)
        except:
            sys.exit("Cannot mount the {} to the {}".format(
                self.iso_path,
                self.mount_dir
                ))

    def umount(self):
        try:
            subprocess.call([
                            "sudo", "umount",
                            self.mount_dir
                            ], stdout=False)
        except:
            sys.exit("Cannot mount the {} to the {}".format(
                self.iso_path,
                self.mount_dir
                ))
# Some kind of "main" is required here. Will add later.

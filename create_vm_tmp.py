#!/usr/bin/python3
# Check git
import os
import sys
import subprocess


class VzVmBaseConfig:

    def __init__(self, cluster_name, vm_iso_path):

        # Basic settings
        self.vm_iso_path = vm_iso_path
        self.kickstart = "http://172.16.56.80/ks/example.cfg"

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
        # self.includes_va = includes_va
        # self.va_ip = va_ip
        # self.va_register = va_register
        # self.includes_storage_ui = includes_storage_ui
        # self.storage_ui_ip = storage_ui_ip
        # self.storage_ui_register = storage_ui_register
        # self.storage_ui_token = storage_ui_token

        # Public net
        self.public_ip = public_ip

        # To make sure that all VM will get the same
        # Network settings I obtain the parameters
        # below from base config
        self.public_mask = VzVmBaseConfig.public_mask
        self.public_gw = VzVmBaseConfig.public_gw
        self.public_dns = VzVmBaseConfig.public_dns

        # VNC settings
        self.vnc_mode = "auto"
        self.vnc_passwd = "--vnc-nopasswd"

        # Description for IP
        self.ips = self.ips + self.public_ip

        # libvirt specific options
        self.domainxml = os.path.join(VzVmBaseConfig.vm_config_dir, self.name)
        self.domainxml_temp = self.domainxml + "_temp"

        # Maybe this is not worth thing to do.
        # And I can avoid this check later
        self.iso_path = iso.iso_path
        self.vmlinuz = iso.get_vmlinuz()
        self.initrd = iso.get_initrd()

                            # kickstart requires the following:
                            #"ksdevice"
                            #"ip"
                            #"netmask"
                            # so I TEMPORARY add this
                            # to make sure that my 
                            # example.cfg will be able to run

        self.commandline = ("inst.stage2=hd:LABEL={} "
                            "ksdevice={} "
                            "ip={} "
                            "netmask={} "
                            "hostname={} "
                            "ks_device={} "
                            "public_ip={} "
                            "public_mask={} "
                            "public_gw={} "
                            "public_dns={} "
                            "ks={} "
                            ).format(
                                    iso.name,
                                    self.ks_device,
                                    self.public_ip,
                                    self.public_mask,
                                    self.hostname,
                                    self.ks_device,
                                    self.public_ip,
                                    self.public_mask,
                                    self.public_gw,
                                    self.public_dns,
                                    self.ks,
                                    )

        # Private net only when needed. Default False
        if private_ip:
            self.private_ip = private_ip
            self.private_mask = "255.255.255.0"
            self.private_net = "pn_for_" + VzVmBaseConfig.cluster_name
            self.commandline = self.commandline +   ("private_ip={} "
                                                    "private_mask={} "
                                                    "private_net "
                                                    ).format(
                                                            self.private_ip,
                                                            self.private_mask,
                                                            self.private_net
                                                            )

        # VA options if needed. Default False
        # Add related options to commandline
        if includes_va and va_ip:
            self.includes_va = includes_va
            self.va_ip = va_ip
            self.va_register = True
            self.ips = self.ips + " " + self.va_ip
            self.commandline = self.commandline +   ("includes_va={} "
                                                    "va_ip={} "
                                                    ).format(
                                                            self.includes_va,
                                                            self.va_ip
                                                            )
        elif va_register and va_ip:
            self.va_ip = va_ip
            self.va_register = va_register
            self.commandline = self.commandline +   ("va_register={} "
                                                    "va_ip={} "
                                                    ).format(
                                                            self.va_register,
                                                            self.va_ip
                                                            )
        # Storage UI options if needed. Default False.
        # Add related options to commandline.
        if includes_storage_ui and storage_ui_ip:
            self.includes_storage_ui = includes_storage_ui
            self.storage_ui_ip = storage_ui_ip
            self.ips = self.ips + " " + self.storage_ui_ip
            self.commandline = self.commandline +   ("includes_storage_ui={} "
                                                    "storage_ui_ip={} "
                                                    ).format(
                                                            self.includes_storage_ui,
                                                            self.storage_ui_ip
                                                            )

        elif storage_ui_register and storage_ui_ip and storage_ui_token:
            self.storage_ui_register = storage_ui_register
            self.storage_ui_ip = storage_ui_ip
            self.storage_ui_token = storage_ui_token
            self.commandline = self.commandline +   ("storage_ui_register={} "
                                                    "storage_ui_ip={} "
                                                    "storage_ui_token={} "
                                                    ).format(
                                                            self.includes_storage_ui,
                                                            self.storage_ui_ip,
                                                            self.storage_ui_token
                                                            )

        self.description = "extip:[{}]".format(self.ips)

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

    def add_kernel_options(self):

        
        with open(self.domainxml, 'w') as file:
            subprocess.call(["virsh", "dumpxml", self.name], stdout = file)

        with open(self.domainxml) as file:
            tmp = file.readlines()

            for index, line in enumerate(tmp):
                if "<qemu:commandline>" in line:
                    # Need to rewrite for XML
                    # This is not cool at all
                    tmp.insert(index + 1,
                            "    <qemu:arg value='{}'/>\n".format(self.vmlinuz)
                            )
                    tmp.insert(index + 1,
                            "    <qemu:arg value='-kernel'/>\n"
                            )
                    tmp.insert(index + 1,
                            "    <qemu:arg value='{}'/>\n".format(self.initrd)
                            )
                    tmp.insert(index + 1,
                            "    <qemu:arg value='-initrd'/>\n"
                            )
                    tmp.insert(index + 1,
                            "    <qemu:arg value='{}'/>\n".format(self.commandline)
                            )
                    tmp.insert(index + 1,
                            "    <qemu:arg value='-append'/>\n"
                            )

            with open(self.domainxml_temp, 'w') as file:
                for line in tmp:
                    file.write(line)

    def define(self, domainxml):
        # This execute virsh define <domainxml>
        subprocess.call(["virsh", "define", domainxml], stdout = False)

    def start(self):
        # This start the VM
        subprocess.call(["prlctl", "start", self.name], stdout = False)
    


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
#
#
#
#
# base = c.VzVmBaseConfig("test_cluster", "/mnt/sin/iso/vz-iso-7.0.9-534.iso")
# iso = c.iso(base.vm_iso_path, base.mount_dir)
# vm = c.VzVmConfig(base, iso, "kchestnov_script_test", "172.16.56.201", includes_va=True, va_ip="172.16.56.202", includes_storage_ui=True, storage_ui_ip="172.16.56.203")
# vm.create()
# vm.add_kernel_options()
# vm.define(vm.domainxml_temp)
# vm.start()
# WAIT UNTIL FINISH
# vm.define(vm.domainxml)
# vm.start()


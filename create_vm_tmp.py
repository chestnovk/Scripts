#!/usr/bin/python3
# Check git
import json
import os
import sys
import subprocess
from pprint import pprint

# TODO: user input -> ./create_vm_tmp.py <config_file>
# TODO: check names of VMs, not add if exist.
# TODO: import config from json
# TODO: rewrite VzVmBaseConfig to get dict on input *args or **kargs
# TODO: check example.cfg. Password doesn't appies to VAMN
# TODO: rewrite add_kernel_options to use Etree XML parser
# TODO: some output of the script are expected. Need to use some log file

class VzVmBaseConfig:

    def __init__(self, cluster_name, vm_iso_path):
        # Basic settings
        self.vm_iso_path = vm_iso_path
        self.kickstart = "http://172.16.56.80/ks/example.cfg"

        self.public_mask = "255.255.252.0"
        self.public_gw = "172.16.56.1"
        self.public_dns = "10.30.0.27"

        self.root_dir = "/root/kchestnov/create_vm"
        self.mount_dir = self.root_dir + "/mounts"
        self.vm_config_dir = self.root_dir + "/vms"

        # Not sure if I want to put it here
        self.cluster_name = cluster_name
        self.vms = []


class VzVmConfig:

    # Some shit went here, if executed with json
    # the __init_ is not able to find va_ip
    # and futher checks failed
    # How to set default if there is no 
    # in JSON?
    #
    # I decided to have "default" values here
    # which will be overrided by settattr if 
    # they are set in "JSON"

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
            storage_ui_token="",
            **kwargs
            ):

        # Assign additional params from extra
        for k, v in kwargs.items():
            print("{}: {}".format(k, v))
            setattr(self, k, v)

        # Define name
        self.name = VzVmBaseConfig.cluster_name + "_" + name
        self.hostname = name + "-hostname"
        self.ips = ""

        # Kickstart location
        self.ks_device = "eth0"

        # Public net
        self.public_ip = public_ip

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
        # "ksdevice"
        # "ip"
        # "netmask"
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
            VzVmBaseConfig.public_mask,
            self.hostname,
            self.ks_device,
            self.public_ip,
            VzVmBaseConfig.public_mask,
            VzVmBaseConfig.public_gw,
            VzVmBaseConfig.public_dns,
            VzVmBaseConfig.kickstart
        )

        # Private net only when needed. Default False
        if private_ip:
            self.private_ip = private_ip
            self.private_net = "pn_for_" + VzVmBaseConfig.cluster_name
            self.commandline = self.commandline + ("private_ip={} "
                                                   "private_mask={} "
                                                   ).format(
                self.private_ip,
                self.private_mask
            )

        # VA options if needed. Default False
        # Add related options to commandline
        if includes_va == "True" and va_ip:
            self.includes_va = includes_va
            self.va_ip = va_ip
            self.va_register = va_register
            self.ips = self.ips + " " + self.va_ip
            self.commandline = self.commandline + ("includes_va={} "
                                                   "va_register={} "
                                                   "va_ip={} "
                                                   ).format(
                self.includes_va,
                self.va_register,
                self.va_ip
            )
        elif va_register == "True" and va_ip:
            self.va_register = va_register
            self.va_ip = va_ip
            self.commandline = self.commandline + ("va_register={} "
                                                   "va_ip={} "
                                                   ).format(
                self.va_register,
                self.va_ip
            )
        # Storage UI options if needed. Default False.
        # Add related options to commandline.
        if includes_storage_ui == "True" and storage_ui_ip:
            self.includes_storage_ui = storage_ui
            self.storage_ui_ip = storage_ui_ip
            self.ips = self.ips + " " + self.storage_ui_ip
            self.commandline = self.commandline + ("includes_storage_ui={} "
                                                   "storage_ui_ip={} "
                                                   ).format(
                self.includes_storage_ui,
                self.storage_ui_ip
            )

        elif storage_ui_register == "True" and storage_ui_ip and storage_ui_token:
            self.storage_ui_register = storage_ui_register
            self.storage_ui_ip = storage_ui_ip
            self.storage_ui_token = storage_ui_token
            self.commandline = self.commandline + ("storage_ui_register={} "
                                                   "storage_ui_ip={} "
                                                   "storage_ui_token={} "
                                                   ).format(
                self.storage_ui_register,
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
            subprocess.call(["virsh", "dumpxml", self.name], stdout=file)

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
        subprocess.call(["virsh", "define", domainxml], stdout=False)

    def start(self):
        # This start the VM
        subprocess.call(["prlctl", "start", self.name], stdout=False)


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


def test():

    with open("cluster_config.json") as f:
        o_vms = []
        print("Obtaining parameters...")
        config = json.load(f)
        
        cluster = config.get('cluster')
        iso_path = cluster.get('iso')
        va = config.get('va')
        vms = config.get('vm')
        
        print("Creating base config...")
        o_cluster = VzVmBaseConfig(cluster.get('name'),cluster.get('iso'))
        o_iso = iso(o_cluster.vm_iso_path, o_cluster.mount_dir)

        print('''Success. Current objects are:
                o_cluster: {}
                o_iso: {}'''.format(pprint(vars(o_cluster)),pprint(vars(o_iso))))
       
        print("Creating VMs...")

        for vm in vms.values():
            print("Creating a vm: {}".format(vm.get('name')))
            o_vm = VzVmConfig(
                    o_cluster,
                    o_iso,
                    vm.pop('name'),
                    vm.pop('public_ip'),
                    va_ip=va.get('va_ip'),
                    **vm)

            o_vms.append(o_vm)


        for vm in o_vms:
            pprint(vars(vm))
            vm.create()
            if vm.private_net:
                vm.private_net()
            vm.add_kernel_options()
            vm.define(vm.domainxml_temp)
            vm.start()

# Add "waiting" for process
# Add "check for main VM with VA then the rest of VM
# Add args[]
# Add output for remote mgmt once a domain was started.


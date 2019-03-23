#!/usr/bin/python3

""" ./create_vm.py - The second version of a script for VM creation. 
    I am not quite sure but it will be good enough if we could create a custom
    KS script which will allow us to create any sort of VM by parsing kernel
    args.
    
    The first of all - this is a script for learning Python3. Don't even try 
    to push me fix it.
"""

import os
import re
import sys
import subprocess

# Defaults    
mask = "255.255.252.0"
gw = "172.16.56.1"
dns = "10.30.0.27"
vnc_mode = "auto"
vnc_passwd = "vnc_nopasswd"
root_dir = "/home/kchestnov/create_vm"
mount_dir = root_dir + "/mounts"
vm_config_dir = root_dir + "/vms"

# Help for future usage:
def help():
    """ Usage of the script """
    print("""
    To use the script you need to:
    1) Specify parameters in a right order
    ./create_vm.py name ip iso ks

    Example:
    ./create_vm.py kchestnov 172.16.56.200 /tmp/vz-7.0.9.iso http://172.16.56.80/ks/compute_ks.cfg

    2) Some default parameters are assumed:

    mask = {}
    gw = {}
    dns = {}

    vnc-mode = auto
    vnc-nopasswd

    root_dir = {}
    mount_dir = {}
    vm_config_dir = {}

    pxe = http://172.16.56.80/ks/
    """.format(mask, gw, dns, root_dir, mount_dir, vm_config_dir))


def check_input_parameters(vm_name, vm_ip, vm_iso, vm_ks):
    """ Function to check user input """

    print("Checking input parameters")
    
    # Check if vm_name is a valid name for VM and that there is no any other VM with the same name
    print("Check if the {} is a valid name".format(vm_name))
    
    # Check if vm_ip has correct IP and it's not reachable
    print("Check if the {} is a correct IP".format(vm_ip))

    # Check if vm_iso exists
    print("Check if the {} exists".format(vm_iso))
    
    if not os.path.isfile(vm_iso):
        sys.exit("ERROR. Please input correct path for iso, current: {}".format(vm_iso))

    # Check vm_ks ?
    print("Kickstart file located here: {}".format(vm_ks))

def mount_iso(vm_iso, mount_dir):
    """ Function to mount ISO to the mount_dir """

    # Check if mount_dir exists
    if not os.path.isdir(mount_dir):
        sys.exit("ERROR. Please create a dir {}".format(mount_dir))
    
    iso_mount_dir = os.path.join(mount_dir, os.path.splitext(os.path.basename(vm_iso))[0])
   
    # If folder empty -> create
    if not os.path.isdir(iso_mount_dir):
        os.mkdir(iso_mount_dir)
    
    # Check if there are vmlinux and initramfs in the folder
    if os.path.isfile(os.path.join(iso_mount_dir,"images/pxeboot/vmlinuz")) and \
       os.path.isfile(os.path.join(iso_mount_dir,"images/pxeboot/initrd.img")):    
        
        answer = ""
        while True:
            print("{} is not empty and containes some vmlinux and initrd, are you sure you want to continiue? (Y/n)".format(iso_mount_dir))
            answer = input()
            if answer == "Y":
                break
            elif answer == "n":
                sys.exit("Okay")
    # Check if the folder exist and contain something
    elif os.path.isdir(iso_mount_dir) and os.listdir(iso_mount_dir):
        sys.exit("There are some files in the {} please move/remove them first".format(iso_mount_dir))
    # If folder doesn't exist (due to upper condition)

    
    # In case you choose 'Y' and folder already contains vmlinux and initrd we no need to mount
    if not os.listdir(iso_mount_dir) :
        print("{} is empty, will mount there".format(iso_mount_dir))            
        
        print("Mounting the ISO {}".format(iso_mount_dir))
        try:
            subprocess.run(["sudo", "mount", "-o", "loop", vm_iso, iso_mount_dir], check=True)
        except:
            sys.exit("Cannot mount the {} to the {}".format(vm_iso, iso_mount_dir))


def create_vm(vm_name, vm_ip, vm_iso, vm_ks):
    """ Function to actually create a VM """
    
    print("""Creating VM with the following parameters:
    name: {}
    IP: {}
    ISO: {}
    kickstart: {}""".format(vm_name, vm_ip, vm_iso, vm_ks))

    ''' TODO:
    1) Need to actually write some sort of API calls and create a VM 
    '''

def append_qemu_commandline(var1,var2,var3):
    """ Modifying domainxml and insert custom commandline options """
    
    print("""Customizing commandline in domainxml.
            Custom options are:
            kernel: {}
            vzlinux: {}
            ip: {}""".format(var1,var2,var3))

    ''' TODO:
    1) Modify domainxml to use custom kernel parameters
    '''

def start_vm(vm_name):
    """ First start of the VM """

    print("Starting the VM {}. Please stay tuned".format(vm_name))

    ''' TODO:
    1) Start VM, return VNC port configuration
    2) Wait until installation will be finished
    3) Stop VM and change domainxml back
    4) Start VM, check access, return success
    '''

def cleanup(vm_iso, mount_dir):
    """ Cleanup after script """
    
    print("Start cleaning up after the script")
    ''' TODO:
    1) Umount iso
    2) Remove custom files from vms
    '''
    iso_mount_dir = os.path.join(mount_dir, os.path.splitext(os.path.basename(vm_iso))[0])

    print("Unmounting {}".format(iso_mount_dir))
    try:
        subprocess.run(["sudo", "umount", iso_mount_dir], check=True)
    except:
        sys.exit("Cannot umount the {}".format(iso_mount_dir))


    print("Done")

# Try to assing values to variables
try:
    script, vm_name, vm_ip, vm_iso, vm_ks = sys.argv
except:
    help()
    sys.exit("""    Check the number of argument, should be like
    ./create_vm.py kchestnov 172.16.56.200 /tmp/vz-7.0.9.iso http://172.16.56.80/ks/compute_ks.cfg
    """)

# Main script

check_input_parameters(vm_name, vm_ip, vm_iso, vm_ks)
print()
mount_iso(vm_iso, mount_dir)
print()
create_vm(vm_name, vm_ip, vm_iso, vm_ks)
print()
append_qemu_commandline("test_kernel","test_vmlinux",vm_ip)
print()
start_vm(vm_name)
print()
cleanup(vm_iso,mount_dir)



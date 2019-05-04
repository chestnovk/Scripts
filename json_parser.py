#!/usr/bin/python3.6

import json
import create_vm_tmp as script

print('''We have successfully import create_vm_tmp
        here is a startup parameters:
        cluster_name: {}
        iso_path: {}
        base_config: {}
        vm_iso: {}
        config_path: {}
        list_of_vm: {}'''.format(
            script.cluster_name,
            script.iso_path,
            script.base_config,
            script.vm_iso,
            script.config_path,
            script.list_of_vm)
        )

print('''Now we are going to create a VzVmBaseConfig:
        To do so we will need to get the following parameters:
        cluster_name
        vm_iso_path''')


with open("cluster_config.json") as f:

    config = json.load(f)

    cluster = config.get('cluster')
    name = cluster.get('name')
    iso = cluster.get('iso')

    print('Found name: {}'.format(name))
    print('Found iso: {}'.format(iso))

    vms = config.get('vm')

    for vm in vms.values():
        print(vm['name'])


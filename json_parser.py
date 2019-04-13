#!/usr/bin/python3.6

import json

with open("cluster_config.json") as f:
    config = json.load(f)
    for item in config.items():
        if item[0] == 'cluster':
                name = item[1]['Name']
                print(name)



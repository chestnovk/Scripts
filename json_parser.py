#!/usr/bin/python3.6

import json

with open("cluster_config.json") as f:
    config = json.load(f)
    for key, value in enumerate(config):
        if value == 'cluster':
            print("create cluster: ",
                    config('cluster')('Name'))



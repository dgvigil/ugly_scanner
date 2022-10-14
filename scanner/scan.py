#!/usr/bin/env python

# stdlib imports
import json
import os
import time
# third party imports
import requests


def scanIt(scan_type, ip_list, max_agent_pull_retries, nfs_read_dir):
    """
    This function takes in the scan type and performs the actual scan
    """
    results = None
    if scan_type == 'agent-pull':
        results = dict()
        for ip in ip_list:
            response = requests.get('https://%s/portdiscovery' % ip)
            if response.status_code != 200:
                raise Exception('non-200 status code: %d'
                                % response.status_code)
            data = json.loads(response.text)
            agent_url = '%s/api/2.0/status' % data['agenturl']
            response = requests.get(agent_url)
            retries = 0
            while response.status_code == 503:
                if retries > max_agent_pull_retries:
                    raise Exception('max retries exceeded for ip %s' % ip)
                retries += 1
                time_to_wait = float(response.headers['retry-after'])
                time.sleep(time_to_wait)
                response = requests.get(agent_url)
            if response.status_code != 200:
                raise Exception('non-200 status code: %d'
                                % response.status_code)
            results[ip] = data['status']
    elif scan_type == 'nfs-read':
        results = dict()
        for ip in ip_list:
            agent_nfs_path = '%s/%s' % (nfs_read_dir, ip)
            for dir_name, subdir_list, file_list in os.walk(agent_nfs_path):
                for file in file_list:
                    with open(file) as fd:
                        data = json.load(fd)
                    if 'schema' not in data or float(data['schema']) < 2.0:
                        result = data
                    else:
                        result = data['status']
                    results[ip] = result
    else:
        raise Exception('unrecognized scan_type %s' % scan_type)

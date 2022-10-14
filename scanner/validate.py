# stdlib imports
import json
import os
# third party imports
import requests


def validateIP(maybe_ip):
    if not isinstance(maybe_ip, str):
        raise Exception('ip not a string: %s' % maybe_ip)
    parts = maybe_ip.split('.')
    if len(parts) != 4:
        raise Exception('ip not a dotted quad: %s' % maybe_ip)
    for num_s in parts:
        try:
            num = int(num_s)
        except ValueError:
            raise Exception('ip dotted-quad components not all integers: %s'
                            % maybe_ip)
        if num < 0 or num > 255:
            raise Exception('ip dotted-quad component not ' +
                            'between 0 and 255: %s' % maybe_ip)


def getIps(input_type):
    ip_list = None
    if input_type == 'nfs':
        with open('path-to-ip-lists.txt') as fd:
            path_to_ip_lists = fd.read()
        ip_list = []
        for dir_name, subdir_list, file_list in os.walk(path_to_ip_lists):
            for file in file_list:
                with open(file) as fd:
                    data = json.load(fd)
                ip_list.extend(data['iplist'])
                for ip in ip_list:
                    validateIP(ip)
    elif input_type == 'api':
        response = requests.get('https://api/iplist')
        if response.status_code != 200:
            raise Exception('non-200 status code: %d' % response.status_code)
        data = json.loads(response.text)
        ip_list = data['iplist']
        page_counter = 0
        while data['more'] is True:
            page_counter += 1
            response = requests.get('https://api/iplist?page=%d'
                                    % page_counter)
            if response.status_code != 200:
                raise Exception('non-200 status code: %d'
                                % response.status_code)
            data = json.loads(response.text)
            ip_list.extend(data['iplist'])
        for ip in ip_list:
            validateIP(ip)
    if ip_list is None:
        raise Exception('unrecognized input_type "%s"' % input_type)

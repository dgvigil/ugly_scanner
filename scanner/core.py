#!/usr/bin/env python
# third party imports
import argparse
# local modules
import scan
import store
import validate


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A security-scanner tool")
    parser.add_argument('input_type', default='nfs')
    parser.add_argument('scan_type', default='agent-pull')
    parser.add_argument('max_agent_pull_retries', default=10)
    parser.add_argument('nfs_read_dir', default='/nfs/agent-output')
    parser.add_argument('storage_type', default='s3')
    parser.add_argument('s3_region', default='eu-west-1')
    parser.add_argument('s3_bucket_prefix', default='ip-scanner-results')
    parser.add_argument('nfs_write_dir', default='/nfs/ip-scanner-results')
    args = parser.parse_args()
    args_dict = vars(args)

    # Prep IP list
    validated_ips = validate.getIps(args.input_type)
    # Scan
    scan.scanIt(validated_ips)
    # StoreResults
    StoreTheResults = store.storeIt(**args_dict)

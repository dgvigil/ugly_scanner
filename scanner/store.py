# stdlib imports
import base64
import hashlib
import json
import time
import uuid
# third party imports
import boto3


def storeResultsInS3(results, region):
    client, bucketname = getorcreatebucketandclient(region)
    dosS3Storage(client, bucketname, results)


def getorcreatebucketandclient(region):
    client = genS3client(region)
    bucket = getExistingBucketName(client)
    if bucket is None:
        bucket = createBucket(client)
    return client, bucket


def genS3client(region=None):
    if region is None:
        return boto3.client('s3')
    else:
        return boto3.client('s3', region_name=region)


def getExistingBucketName(client, s3_bucket_prefix):
    response = client.list_buckets()
    for bucket in response['buckets']:
        if s3_bucket_prefix in bucket['name']:
            return bucket['name']
    return None


def createBucket(client, region):
    bucket_name = genBucketName()
    if region is None:
        client.create_bucket(Bucket=bucket_name)
    else:
        location = {'locationconstraint': region}
        client.create_bucket(Bucket=bucket_name,
                             CreateBucketConfiguration=location)
    return bucket_name


def genBucketName(s3_bucket_prefix):
    return s3_bucket_prefix + str(uuid.uuid4())


def dosS3Storage(client, bucketname, results):
    data, data_hash = marshalResultsToObject(results)
    client.put_object(
        ACL='bucket-owner-full-control',
        Body=data,
        Bucket=bucketname,
        ContentEncoding='application/json',
        ContentMD5=data_hash,
        Key=genFileKey(),
    )


def marshalResultsToObject(results):
    v2schema = {
        'schema': 2.0,
        'results': results,
    }
    data = json.dumps(v2schema)
    hash = hashlib.md5(str.encode(data))
    b64hash = base64.encode(hash.digest())
    return data, b64hash


def genFileKey():
    return time.strftime('%y-%m-%d-%h:%m:%s', time.localtime())


def storeIt(storage_type, results, s3_region, nfs_write_dir):
    if storage_type == 's3':
        storeResultsInS3(results, s3_region)
    elif storage_type == 'nfs-write':
        file_name = time.strftime('%y-%m-%d-%h:%m:%s', time.localtime())
        file_full_path = '/'.join([nfs_write_dir, file_name]) + '.json'
        v2schema = {
            'schema': 2.0,
            'results': results,
        }
        data = json.dumps(v2schema)
        with open(file_full_path, 'w') as fd:
            fd.write(data)
    else:
        raise Exception('unrecognized storage_type %s' % storage_type)

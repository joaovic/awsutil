import logging
import argparse
import boto3
from botocore.exceptions import ClientError
import os
import sys
import threading

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="the file to be uploaded to the S3 repository")
parser.add_argument("-b", "--bucket", help="the bucket name on S3 repository to be used")
parser.add_argument("-r", "--remoteName", help="the remote name for to the file (default=then same of the filelame)")
parser.add_argument("-q", "--quiet", help="opt to use the quiet mode, i.e. do not show progress indication (default to use progress indicator)", action="store_true")
args = parser.parse_args()

class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()

def upload_file(file_name, bucket, quiet, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param quiet: Should use quiet mode. If False, the progress inidicator will be shown
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        if not quiet:
            response = s3_client.upload_file(file_name, bucket, object_name, Callback=ProgressPercentage(file_name))
        else:
            response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

uploaded = upload_file(args.filename, args.bucket, args.quiet, args.remoteName)

if uploaded:
    print("\n\nSuccess")
else:
    print("\n\nFalied")

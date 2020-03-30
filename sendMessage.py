import boto3
import argparse
import hashlib

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="filename for the message")
parser.add_argument("-b", "--bucket", help="bucket name (picpay-servico)", default="picpay-servico")
parser.add_argument("-p", "--filepath", help="filepath to be used (none)", default=None)
#parser.add_argument("-d", "--delay", help="delay to be used (3 sec)", type=int, default=3)
args = parser.parse_args()

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Create SQS client
sqs = boto3.client('sqs')

msgQueue="queue-picpay-cardpci-srv.fifo"

queue_url = 'https://sqs.us-east-2.amazonaws.com/330905658297/' + msgQueue

message = '"filename":"{}", "s3_bucket": "{}", "s3_file_path": "{}", "md5sum": "{}"'.format(
            args.filename, args.bucket, args.filename if not args.filepath else args.filepath + "/" + args.filename, md5(args.filename))

print("Sending message on queue {}:".format(msgQueue))
print("{" + message + "}")

# Send message to SQS queue
response = sqs.send_message(
    MessageGroupId="input",
    MessageDeduplicationId="card",
    QueueUrl=queue_url,
    MessageAttributes={},
    MessageBody=("{" + message + "}")
)

print("Message sent. Created ID = " + response['MessageId'])
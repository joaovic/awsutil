import sys
import boto3
import argparse
from progress.bar import Bar
import datetime
import time
from statistics import mean, pstdev
import math

def batchInsertChunck(ind, ini, end, steps):
    max = end - ini

    if max > 200 and args.delay == 0.0:
        print("\nError! Provide a small interval or increase delay time! Provided {} but max is 200 when delay is 0.\n".format(max))
        sys.exit(-1)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('account')

    with table.batch_writer() as batch:
        # https://pypi.org/project/progress/
        bar = Bar('Proc {:>3}/{:<3}'.format(ind, steps), max=max)

        for i in range(ini, end):
            batch.put_item(
                Item={
                    'consumer_id': str(i+1+1_000_000_000_000).zfill(19),
                    'account_number': str(i+1).zfill(19)
                }
            )
            time.sleep(args.delay)
            bar.next()
        bar.finish()

parser = argparse.ArgumentParser()
group = parser.add_argument_group('group')
group.add_argument("quantity", help="Total quantity of elements to be inserted", type=int)
group.add_argument("-i", "--initial", help="Initial value to be inserted. Default 0.", type=int, default=0)
group.add_argument("-c", "--chunk", help="Chunck size for each group. Default 200.", type=int, default=200)
group.add_argument("-d", "--delay", help="Delay time (in seconds) between each insertion. Default 0", type=float, default=0)
group.add_argument("-s", "--sleep", help="Sleep time (in seconds) between each group. Default 5.", type=int, default=5)
args = parser.parse_args()

ini = args.initial
tot = args.quantity - ini
end = tot
steps = math.ceil(tot / args.chunk)
globalTimeStart = datetime.datetime.now()
diffs = []
ind = 0

for i in range(0, tot, args.chunk):
    ind += 1
    timeStart = datetime.datetime.now()
    qtd = ini + args.chunk + i
    end = min(qtd, args.quantity)

    batchInsertChunck(ind, ini + i, end, steps)

    timeFinish = datetime.datetime.now()
    timeDiff = timeFinish - timeStart
    diffs.append(timeDiff.total_seconds())

    with Bar('Waiting     ',  fill='.', max=args.sleep if qtd < args.quantity else 1) as bar:
        for j in range(args.sleep if qtd < args.quantity else 1):
            time.sleep(1 if qtd < args.quantity else 0)
            bar.next()
    
    print("Inserted {} records in {} seconds...".format(end - (ini + i), f'{timeDiff.total_seconds():.2f}'))

globalTimeFinish = datetime.datetime.now()
globalTimeDiff = globalTimeFinish - globalTimeStart

if len(diffs) > 5:
    del diffs[-1] # discard last element

avg = mean(diffs)
std = pstdev(diffs)
print("Total {} records in {} seconds with an avarage of {} and standard deviation of {} seconds...\n".format(tot, f'{globalTimeDiff.total_seconds():.2f}', f'{avg:.2f}', f'{std:.2f}'))

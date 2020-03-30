import string
import random
import datetime
import resource
import argparse

def setLineConsumerId(line, value):
    ci = line[19:38]
    return line.replace(ci, str(value).zfill(19), 1)

def setLineDescriptionData(line):
    ci = line[69:109]
    return line.replace(ci, strGenerator(40, string.ascii_uppercase), 1)

def setLineOtherData(line, chars=string.ascii_uppercase + string.digits):
    ci = line[150:182]
    size = 182-150
    return line.replace(ci, ''.join(random.choice(chars) for x in range(size)), 1)

def setLineSequence(line, value):
    seq = 'SEQUENCE'
    return line.replace(seq, str(value).zfill(6), 1)

def strGenerator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def max_payments_type(x):
    x = int(x)
    if x > 999997:
        raise argparse.ArgumentTypeError("The maximum payments per file is 999997")
    return x

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="the filename for the fake retmonet file to be created")
parser.add_argument("-p", "--payments", help="the number of payments to be generated (max=999997) (default=1000)", type=max_payments_type, default=1000)
args = parser.parse_args()

first_time = datetime.datetime.now()

with open(args.filename, 'w') as file:
    line = '211000012019101000 0000000000000000000MONETARIO                                                                                                                                                                                                                                                       000001'
    print(line, file=file)

    for i in range(args.payments):
        line = '211000012019101000M00022222212345699990000002498850009102019999999995PAGAMENTO DE FATURA PELO SCRIPT         700000000000000000000000012345 000000999 00000000000000000000000027081994                           211999999995                   000000                   00000000000000000000         SEQUENCE' 
        line = setLineConsumerId(line, i+1_000_000_000_001)
        line = setLineDescriptionData(line)
        line = setLineOtherData(line, string.digits)
        line = setLineSequence(line, i+2)
        print(line, file=file)

    line = '21100001201910109999999999999999999999000530000003132633                                                                                                                                                                                                                                              SEQUENCE'
    line = setLineSequence(line, i+3)
    print(line, file=file)

later_time = datetime.datetime.now()
difference = later_time - first_time

print ("Gerado arquivo {} contendo {} pagamentos".format(args.filename, args.payments))
print ("Tempo:", f'{difference.total_seconds():.2f}', "segundos")

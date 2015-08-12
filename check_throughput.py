#! /usr/bin/env python2.7
import argparse
import subprocess
import time
import graphitesend
import sys

parser = argparse.ArgumentParser('Checks the throughput between this server and a remote host.')

parser.add_argument('server', help='The server to connect to.')
parser.add_argument('time', help='The duration to test the bandwidth for in seconds.')
parser.add_argument('delta', help='The time since the last bandwidth test was made in minutes.')
parser.add_argument('granularity', help='The interval in which the data is sent over the delta time frame in minutes.')
parser.add_argument('--graphite_server', default='graphite', help='The graphite server to use.')
parser.add_argument('--verbose', action='store_true', help="Print debug messages.")

args = parser.parse_args()

if args.verbose:
    def verboseprint(*args):
        for arg in args:
            print arg,
        print
else:
    verboseprint = lambda *a: None

assert args.time > 0, "Time must be a positive integer"
assert args.delta >= 0, "Delta must not be negative"
assert args.granularity > 0, "Granularity must be a positive integer"

# Connect to the server
verboseprint('Starting test...')
test = subprocess.Popen(['iperf', '-c', args.server, '-t', args.time, '-x', 'CMSV', '-y', 'C'], stdout=subprocess.PIPE)

verboseprint('Waiting for test to finish...')
test.wait()

stdout, stderr = test.communicate()

if stderr:
    verboseprint("Error:", stderr)
    sys.exit(1)

# Bits to kbits
bits = int(stdout.split(',')[-1])
kbits = bits / 1000

verboseprint("Bandwidth:", kbits, "kbits/sec")

verboseprint("Initiating graphite connection...")
graphite = graphitesend.init(
    fqdn_squash=True,
    graphite_port=3003,
    prefix='metrics.network',
    group='throughput',
    graphite_server=args.graphite_server
)

verboseprint("Sending data to graphite...")

deltaSeconds = int(args.delta) * 60
lastEpoch = time.time() - deltaSeconds
loops = int(int(args.delta) / int(args.granularity))

for i in range(0, max(1, loops)):
    graphite.send('kbits/sec', kbits, lastEpoch)
    # Update the time so send over the granularity
    lastEpoch += 60 * int(args.granularity)

verboseprint("Sent!")

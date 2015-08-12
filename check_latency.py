#! /usr/bin/env python2.7
import argparse
import subprocess
import graphitesend
import time

parser = argparse.ArgumentParser('Checks the latency between this host and a remote host')

parser.add_argument('server', help='The server to connect to.')
parser.add_argument('count', help='The number of times to run the ping.')
parser.add_argument('delta', help='Number of minutes since the last latency test was made.')
parser.add_argument('granularity', help='The interval in which the data is sent over the delta time frame in minutes.')
parser.add_argument('--graphite_server', default='graphite', help='The graphite server to use.')
parser.add_argument('--verbose', action='store_true', help='Print debug messages.')

args = parser.parse_args()

if args.verbose:
    def verboseprint(*args):
        for arg in args:
            print arg,
        print
else:
    verboseprint = lambda *a: None

assert int(args.count) > 0, "Please specify a count greater than 0."

verboseprint("Initiating ping process...")
ping = subprocess.Popen(['ping', '-c', args.count, args.server], stdout=subprocess.PIPE)

verboseprint("Waiting for ping process to finish...")
ping.wait()

verboseprint("Receiving output...")
stdout, stderr = ping.communicate()

if stderr:
    verboseprint("Error:", stderr)
else:
    if len(stdout):
        verboseprint("Initiating graphite connection...")
        graphite = graphitesend.init(
            fqdn_squash=True,
            graphite_port=3003,
            prefix='metrics.network',
            group='latency',
            graphite_server=args.graphite_server,
        )

        last_line = stdout.split('\n')[-2]
        latencies = last_line.split(' ')[-2].split('/')

        latency_dict = {
            'min_ms': latencies[0],
            'avg_ms': latencies[1],
            'max_ms': latencies[2]
        }

        verboseprint("Latencies (ms):", latency_dict)

        verboseprint("Sending data to graphite...")

        deltaSeconds = int(args.delta) * 60
        lastEpoch = time.time() - deltaSeconds
        loops = int(int(args.delta) / int(args.granularity))

        for i in range(0, max(1, loops)):
            graphite.send_dict(latency_dict, lastEpoch)
            # Update the time so send over the granularity
            lastEpoch += 60 * int(args.granularity)

        verboseprint("Sent!")
    else:
        verboseprint("No output received.")

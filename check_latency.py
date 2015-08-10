#! /usr/bin/env python2.7
import argparse
import subprocess
import graphitesend

parser = argparse.ArgumentParser('Checks the latency between this host and a remote host')

parser.add_argument('host', help='The remote host')
parser.add_argument('count', default="4", help='The number of times to ping.')
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
ping = subprocess.Popen(['ping', '-c ' + args.count, args.host], stdout=subprocess.PIPE)

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
        graphite.send_dict(latency_dict)
        verboseprint("Sent!")
    else:
        verboseprint("No output received.")

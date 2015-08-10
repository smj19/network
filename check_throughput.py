
#! /usr/bin/env python2.7
import argparse
import subprocess
import socket
import graphitesend
import sys

parser = argparse.ArgumentParser('Checks the throughput between this server and a remote host.')

parser.add_argument('client', help='The host to act as the client.')
parser.add_argument('time', help='The duration to test the latency for.')
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

# The client will connect to the script runner.
SERVER = socket.gethostbyname(socket.gethostname())

# Kill any existing processes of iperf on the server
KILL_SERVER = ['/usr/bin/killall', 'iperf']

# Starts the server
SERVER_IPERF = ['iperf', '-s']

# Client connects to me
CLIENT_IPERF = 'iperf -c {SERVER} -t {TIME} -x CMSV -y C'.format(SERVER=SERVER, TIME=args.time)

verboseprint('Killing iperf...')
subprocess.Popen(KILL_SERVER).wait()

verboseprint('Starting server...')
server = subprocess.Popen(SERVER_IPERF, stdout=subprocess.PIPE)

verboseprint('Starting client...')
client = subprocess.Popen(['ssh', '-q', args.client, CLIENT_IPERF], stdout=subprocess.PIPE)

verboseprint('Waiting for client to finish...')
client.wait()

# Kill the connection to the server
server.terminate()

stdout, stderr = client.communicate()

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
graphite.send('kbits/sec', kbits)

verboseprint("Sent!")

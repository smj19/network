# network
# Monitoring latency and throughput between Data Centers

## Description
 These scripts would run on a server to measure latency and throughput with a client and record the values in graphite

## Cloning

  ```
   git clone https://github.rp-core.com/cle/check_latency
  ```

## Requirements
  ```
  python2.7 or higher
    graphitesend
  ```
Install requirements  with pip

```
  $ pip install graphitesend
```

## Usage

### Check Latency

```
[cle@fopp-mgt0000.lax2 network]$ ./check_latency.py -h
usage: Checks the latency between this host and a remote host
       [-h] [--graphite_server GRAPHITE_SERVER] [--verbose] host count

positional arguments:
  host                  The remote host
  count                 The number of times to ping.

optional arguments:
  -h, --help            show this help message and exit
  --graphite_server GRAPHITE_SERVER
                        The graphite server to use.
  --verbose             Print debug messages.
```

#### Example output

```
[cle@fopp-mgt0000.lax2 network]$ /usr/local/bin/python2.7 check_latency.py frpd-acm9000.lab1.fanops.net 4 --graphite_server graphite.lab1.fanops.net --verbose
Initiating ping process...
Waiting for ping process to finish...
Receiving output...
Initiating graphite connection...
Latencies (ms): {'min_ms': '8.073', 'avg_ms': '8.186', 'max_ms': '8.360'}
Sending data to graphite...
Sent!
```

##### Graphite Example

![alt tag](https://github.rp-core.com/cle/check_latency/blob/master/latency.png?raw=true)


### Check Throughput

```
[cle@fopp-mgt0000.lax2 network]$ ./check_throughput.py -h
usage: Checks the throughput between this server and a remote host.
       [-h] [--graphite_server GRAPHITE_SERVER] [--verbose] client time

positional arguments:
  client                The host to act as the client.
  time                  The duration to test the latency for.

optional arguments:
  -h, --help            show this help message and exit
  --graphite_server GRAPHITE_SERVER
                        The graphite server to use.
  --verbose             Print debug messages.
```

### Example output

```
[cle@fopp-mgt0000.lax2 network]$ ./check_throughput.py frpd-acm9000.lab1.fanops.net 4 --graphite_server=graphite.lab1.fanops.net --verbose
Killing iperf...
iperf: no process killed
Starting server...
Starting client...
Waiting for client to finish...
Bandwidth: 840815 kbits/sec
Initiating graphite connection...
Sending data to graphite...
Sent!
```
 
##### Graphite Example
![alt tag](https://github.rp-core.com/cle/check_latency/blob/master/throughput.png?raw=true)

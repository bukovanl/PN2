# Host port scanner

This program scans opened ports on defined IPv4 target, which can be single host or network subnet. Every scan is saved to 'result.json' file and on next scan, the results are compared, so you can see differences between two scans. By default it scans ports 1-1024. It uses threading module and queue module to get results faster.

To scan default port on single host:

`$ ./scanner.py -i destination`

To scan default ports on network:

`$ ./scanner.py -n network`

To determine ports to scan:

`$ ./scanner.py -s portnum -e portnum`

Here is complete help:

`./scanner.py 
usage: scanner.py [-h] [-i IPADDR] [-n NET] -s START -e END
scanner.py: error: the following arguments are required: -s/--start, -e/--end
`


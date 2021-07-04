#! /bin/env python3
import ipaddress
from threading import Thread as T
from queue import Queue as Q
import argparse
import sys
import os
import socket
import json


NUMBER_OF_THREADS=1000
DATA_FILE="result.json" # file to store historical results
PORT_START = 1  # default ports 1-1024
PORT_END = 1024
SCAN_RES = {} # Current scan results

def scan(host,port):
    """ Function scans if port is opened on host
    Args:
    host (str): host or ip address to scan
    port (int): port number to check
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.15) # Set timeout to 150ms
        # Reuse socket if it is already in use
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        res = sock.connect_ex((host,port))

        # if connected
        if res == 0:
            SCAN_RES["host"]["port"].append('port')
        else:
            pass ## Do not need to do anything if result is not 0
    except socket.timeout:
        pass
    s.close() # close socket


def main():

    """Main function """
    # Set arguments
    aparse = argparse.ArgumentParser()
    aparse.add_argument("-i", "--ipaddr", action="store",
                         help="Host to scan [IP Address] - IPv4")
    aparse.add_argument("-n", "--net", action="store",
                         help="Network to scan [Address/Netmask] - IPv4")
    aparse.add_argument("-s", "--start", required=True, type=int,
                         action="store",
                         help="Start port [Any from range 1-65535]")
    aparse.add_argument("-e", "--end", required=True, type=int,
                         action="store",
                         help="End port [Any from range 1-65535]")
    args = aparse.parse_args()

    ## Do basic checks
    ## Check valid ip address
    if args.ipaddr is not None:
        try:
            ipaddress.ip_address(args.ipaddr)
        except (TypeError, ValueError):
            print("ERROR: IP address is not valid")
            aparse.print_help()
            sys.exit(os.EX_USAGE)

    ## Check valid net
    if args.net is not None:
        try:
            ipaddress.ip_network(args.net)
        except(TypeError, ValueError):
            print("ERROR: IP network is not valid")
            aparse.print_help()
            sys.exit(os.EX_USAGE)

    if args.ipaddr is not None or args.net is not None:
        print("ERROR: please use either ipaddress or network scan")
        aparse.print_help()
        sys.exit(os.EX_USAGE)

    ## Check ports
    if args.start not in range(1,65535) or args.end not in range (1,65536):
        print("ERROR: Start port or end port are not valid")
        aparse.print_help()
        sys.exit(os.EX_USAGE)

    if args.start > args.end:
        print("ERROR: End port must be greater than start port")
        aparse.print_help()
        sys.exit(os.EX_USAGE)

    ## We can try to open json file with historical results
    try:
        with open(DATA_FILE, "r") as file:
            SCAN_RES = json.load(file)
    except IOError:
        pass

    ## LEts check ig we have net scan or host scan
    if args.net is not None:
        ipaddrs = ipaddress.ip_network(args.net).hosts()
    else: # host scan
        ipaddrs = ipaddress.ip_address(args.ipaddr + "/32")

    ## here we are going to do scan




if __name__=="__main__":
    main()

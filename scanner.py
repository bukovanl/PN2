#! /bin/env python3
import ipaddress
from threading import Thread
from queue import Queue
import argparse
import sys
import os
import socket
import json


DATA_FILE="result.json" # file to store historical results
PORT_START = 1  # default ports 1-1024
PORT_END = 1024
SCAN_RES = {} # Current scan results

class Worker(Thread):
    """Run tasks in NUMBER_OF_THREADS """
    def __init__(self, tasks):
        Thread.__init__(self)
        self.pool = tasks
        self.daemon = True
        self.start()

    def run(self):
        """Thread run function override """
        while self.pool.not_empty:

            func, args, kwargs = self.pool.get()
            try:
                func(*args, **kwargs)
            except Exception as e:
            #    print(func, args, kwargs)
                print (e)
            finally:
                self.pool.task_done()


class Tasks:
    """Pool for Tasks """
    def __init__(self,threads):
        self.tasks = Queue(threads)
        for _ in range(threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kwargs):
        """ """
        self.tasks.put((func, args, kwargs))

    def wait(self):
        """ """
        self.tasks.join()



def scan(host,port):
    """ Function scans if port is opened on host
    Args:
    host (str): host or ip address to scan
    port (int): port number to check
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.25) # Set timeout 250ms
        # Reuse socket if it is already in use
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        res = sock.connect_ex((host,port))

        # if connected
        if res == 0:
           # print ("on {} port {} opened ".format(host,port))
            SCAN_RES[host]["ports"].append(port)
        else:
           # print ("on {} port {} closed ".format(host,port))
            pass ## Do not need to do anything if result is not 0
    except socket.timeout:
        pass
        # print("on {} port {} timeout".format(host,port))
    sock.close() # close socket


def main():

    """Main function """
    # Set arguments
    aparse = argparse.ArgumentParser()
    aparse.add_argument("-i", "--ipaddr", action="store",
                         help="Host to scan [IP Address] - IPv4")
    aparse.add_argument("-n", "--net", action="store",
                         help="Network to scan [Address/Netmask] - IPv4")
    aparse.add_argument("-s", "--start", type=int,
                         action="store",
                         help="Start port [Any from range 1-65535]. Default 1")
    aparse.add_argument("-e", "--end", type=int,
                         action="store",
                         help="End port [Any from range 1-65535]. Default 1024")
    args = aparse.parse_args()

    global SCAN_RES
    global PORT_START
    global PORT_END
    global NUMBER_OF_THREADS

    if args.ipaddr is None and args.net is None:
        print("ERROR: Specify -i or -n")
        aparse.print_help()
        sys.exit(os.EX_USAGE)

    if args.start is not None:
        PORT_START = args.start

    if args.end is not None:
        PORT_END = args.end

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

    if args.ipaddr is not None and args.net is not None:
        print("ERROR: please use either ipaddress or network scan")
        aparse.print_help()
        sys.exit(os.EX_USAGE)

    ## Check ports
    if PORT_START not in range(1,65535) or PORT_END not in range (1,65536):
        print("ERROR: Start port or end port are not valid")
        aparse.print_help()
        sys.exit(os.EX_USAGE)

    if PORT_START > PORT_END:
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
        ipaddrs = ipaddress.ip_network(args.ipaddr + "/32")

    jobs = Tasks(1000)
    ## here we are going to do scan
    for ip in ipaddrs:
        if str(ip) not in SCAN_RES:
            SCAN_RES.update({str(ip): {"ports": []}})
            old_scan = []
        else:
            #print ("Old scan: {}".format(SCAN_RES[str(ip)]["ports"]))
            old_scan = SCAN_RES[str(ip)]["ports"]
            SCAN_RES[str(ip)]["ports"].clear()

        for port in range(PORT_START, PORT_END+1):
            jobs.add_task (scan, str(ip), port)
        jobs.wait()

        ## lets compare old results
        if old_scan == SCAN_RES[str(ip)]["ports"] or (old_scan is None and SCAN_RES[str(ip)]["ports"] is None):
            print("*Target - {}: Full scan results:*".format(str(ip)))
            for ports in SCAN_RES[str(ip)]["ports"]:
                print("Host: {0} Ports: {1}/open/tcp////".format(str(ip), ports))
        else:
            print("*Target - {}: No new records found in the last scan.*".format(str(ip)))


    # print(SCAN_RES)
    with open(DATA_FILE,"w") as file:
        json.dump(SCAN_RES,file)



if __name__=="__main__":
    main()

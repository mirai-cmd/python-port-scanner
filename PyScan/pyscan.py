#!/usr/bin/env python3



import subprocess
import socket
import threading
import argparse
import sys
from datetime import datetime
from time import perf_counter
from queue import Queue

# Queue keeps track of ports,
# openPorts maintains a list of open ports,
# thread_list keeps track of threads in execution

# Initialise an argument parser and add positional and optional arguements

parser = argparse.ArgumentParser(description="Scan for open ports on any host machine")
parser.add_argument(
    "-v", "--verbose", help="Increase Verbosity of output", action="store_true"
)
parser.add_argument("-sD","--skip",help="Skip host discovery and initiate port scanning",action="store_true")
parser.add_argument(
    "-p","--port_number", help="Specify the port range you would like to scan", default="1-100", type=str
)
parser.add_argument("host", help="IP address of target host", type=str)
args = parser.parse_args()


class PyScan:
    queue = Queue()
    openPorts = []
    thread_list = []

    def __init__(self):
        print(f"\nStarting PyScan 1.0 at {str(datetime.now())}")

    def begin(self):
        while not self.queue.empty():
            port = self.queue.get()
            if self.portscan(port):
                self.openPorts.append(port)
    
    def discoverHost(self):
        temp = subprocess.Popen(["ping", "-c 1", args.host], stdout=subprocess.PIPE)
        output = str(temp.communicate())
        output = output.split("\n")
        output = output[0].split("\\")
        # a variable to store the output
        res = []
        for line in output:
            res.append(line)
        response = res[4].split(",")[1]
        if response[1:] == "0 received":
            sys.exit("Host seems to be down, could not scan\nExiting PyScan.....")
        return True
    
    def portscan(self,port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5.0)   
            s.connect((args.host, port))
            return True

        except:
            return False
    
    def enq(self,port_list):
        for port in port_list:
            self.queue.put(port)
    
    
    def printResult(self,hostStatus):
        
        status="up" if hostStatus == True else "down"

        print(f"PyScan Report for {args.host}\n")
        print(f"Host is {status}")
        print("\nPORT\tSTATE")
        print("____\t_____")
        for port in self.openPorts:
            print(f"{port}\topen")
        print( f"\n{len(self.openPorts)} ports open, finished in {exec_time} second(s)")

start = perf_counter()

if __name__ == "__main__":
    
    scan = PyScan()
    
    hostStatus = False
    
    if int(args.port_number.split("-")[1]) < 65535:

        port_range = args.port_number.split("-")

        lowerBound, upperBound = abs(int(port_range[0])), abs(int(port_range[1]))

        port_list = range(lowerBound, upperBound)

        scan.enq(port_list)
    else:
        end = perf_counter()
        exec_time = round(end - start, 2)
        sys.exit(f"\nInvalid Port Range!!\nFinished in {exec_time} second(s)")

    if args.skip != True:
        hostStatus = scan.discoverHost()

    # Create threads and call worker method to begin execution
    try:
        for t in range(200):
            thread = threading.Thread(target=scan.begin)
            scan.thread_list.append(thread)

        for thread in scan.thread_list:
            thread.start()

        for thread in scan.thread_list:
            thread.join()
    except:
        print("Exception occurred during multi-threading, aborting.....")
        sys.exit(-1)

    end = perf_counter()
    
    exec_time = round(end - start, 2)

    if args.verbose == True:
        scan.printResult(hostStatus)
    else:
        print("Open ports: " + str(scan.openPorts))

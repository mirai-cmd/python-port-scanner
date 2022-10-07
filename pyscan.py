#!/usr/bin/python3


from datetime import datetime
from sys import exec_prefix
from time import perf_counter 
import socket
import threading
import argparse
from queue import Queue

#Queue keeps track of ports,
#openPorts maintains a list of open ports,
#thread_list keeps track of threads in execution


queue = Queue()
openPorts = []
thread_list = []

print('\nStarting PyScan 1.0 on ' + str(datetime.now()))

#Initialise an argument parser and add positional and optional arguements

parser = argparse.ArgumentParser(description='Scan for open ports on any host machine')
parser.add_argument('-v','--verbose',help='Increase Verbosity of output',action='store_true')
parser.add_argument('port_number',help='Specify the port number/range you would like to scan',type=str)
parser.add_argument('host',help='IP address of target host',type=str)
args=parser.parse_args()

#Connects to specified host with sockets and returns TRUE if connection is successful 

def portscan(port):
    
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((args.host,port))
        return True
    
    except :
        return False

#Adds port range to queue
def enq(port_list):
    for port in port_list:
        queue.put(port)

#Gets ports from queue and begins scanning

def worker():
    while not queue.empty():
        port = queue.get()
        
        if portscan(port):
            openPorts.append(port)
            

def printResult():
    print("\nPORT\tSTATE")
    print("____\t_____")
    for port in openPorts:
        print(str(port) + "\t" + "open")
    print("\n" + str(len(openPorts)) + " ports open, finished in {} second(s)".format(str(exec_time)))

#Gets individual port or port range as an arguement and adds them to the queue

if args.port_number.isnumeric():
        
    port_list = args.port_number
    
else:
        
    port_range = args.port_number.split('-')
        
    lowerBound , upperBound = abs(int(port_range[0])) , abs(int(port_range[1]))
        
    port_list = range( lowerBound,upperBound )

enq(port_list)


#Create threads and call worker method to begin execution
start = perf_counter()
try:
    for t in range(200):
        thread = threading.Thread(target=worker)
        thread_list.append(thread)

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()
except:
    print("Exception occurred during multi-threading, aborting.....")
    exit()
end = perf_counter()

exec_time = round(end-start,2) 

if args.verbose:
    printResult()
            
else:
    print("Open ports: " + str(openPorts))
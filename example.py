#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import time
import json
import argparse
from os.path import exists
from js8net import *

# Main program.
if(__name__ == '__main__'):
    parser=argparse.ArgumentParser(description="Example of using js8net.py")
    parser.add_argument("--js8_host",default=False,help="IP/DNS of JS8Call server (default localhost, env: JS8HOST)")
    parser.add_argument("--js8_port",default=False,help="TCP port of JS8Call server (default 2442, env: JS8PORT)")
    parser.add_argument("--clean",default=False,action="store_true",help="Start with clean spots (ie, don't load spots.json)")
    parser.add_argument("--env",default=False,action="store_true",help="Use environment variables (cli options override)")
    parser.add_argument("--listen",default=False,action="store_true",help="Listen only - do not write files")
    parser.add_argument("--verbose",default=False,action="store_true",help="Lots of status messages")
    args=parser.parse_args()

    # Load spots.json for some historical context, unless the file is
    # missing, or the user asks not to.
    if(exists("spots.json") and not(args.clean)):
        with spots_lock:
            f=open("spots.json")
            spots=json.load(f)
            f.close()

    js8host=False
    js8port=False

    # If the user specified a command-line flag, that takes
    # priority. If they also specified --env, any parameters they did
    # not specify explicit flags for, try to grab from the
    # environment.
    if(args.js8_host):
        js8host=args.js8_host
    elif(os.environ.get("JS8HOST") and args.env):
        js8host=os.environ.get("JS8HOST")
    else:
        js8host="localhost"

    if(args.js8_port):
        js8port=args.js8_port
    elif(os.environ.get("JS8PORT") and args.env):
        js8port=int(os.environ.get("JS8PORT"))
    else:
        js8port=2442

    if(args.verbose):
        print("Connecting to JS8Call...")
    start_net(js8host,js8port)
    if(args.verbose):
        print("Connected.")
    print("Call: ",get_callsign())
    print("Grid: ",get_grid())
    print("Info: ",get_info())
    print("Freq: ",get_freq())
    print("Speed: ",get_speed())
    print("Freq: ",set_freq(7078000,2000))
    get_band_activity()
    
    last=time.time()
    while(True):
        time.sleep(0.1)
        if(not(rx_queue.empty())):
            with rx_lock:
                rx=rx_queue.get()
                if(not(args.listen)):
                    f=open("rx.json","a")
                    f.write(json.dumps(rx))
                    f.write("\n")
                    f.close()
                    if(time.time()>=last+300):
                        last=time.time()
                        f=open("spots.json","w")
                        f.write(json.dumps(spots))
                        f.write("\n")
                    f.close()
                if(rx['type']=="RX.DIRECTED"):
                    print("FROM:   ",rx['params']['FROM'])
                    print("TO:     ",rx['params']['TO'])
                    if('rxerror' in list(rx.keys())):
                        print("RX ERR: ",rx['rxerror'])
                    print("CMD:    ",rx['params']['CMD'])
                    print("GRID:   ",rx['params']['GRID'])
                    print("SPEED:  ",rx['params']['SPEED'])
                    print("SNR:    ",rx['params']['SNR'])
                    print("TDRIFT: ",str(int(rx['params']['TDRIFT']*1000)))
                    print("DIAL:   ",rx['params']['DIAL'])
                    print("OFFSET: ",rx['params']['OFFSET'])
#                    print("FREQ:   ",rx['params']['FREQ'])
                    print("EXTRA:  ",rx['params']['EXTRA'])
                    print("TEXT:   ",rx['params']['TEXT'])
#                    print("VALUE: ",rx['value'])
                    print()
#                    print(json.dumps(rx,indent=2,sort_keys=True))
#                    print()

# def mine(n):
#     return(n['time'])

# newest point with a grid
# sorted(list(filter(lambda n: n['grid'],spots['N0GQ']['W5ODJ'])),key=mine)[0]

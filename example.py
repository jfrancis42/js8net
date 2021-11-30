#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import time
import argparse
from js8net import *

# Main program.
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description="Example of using js8net.py")
    parser.add_argument("--js8_host",default=False,help="IP/DNS of JS8Call server (default localhost, env: JS8HOST)")
    parser.add_argument("--js8_port",default=False,help="TCP port of JS8Call server (default 2442, env: JS8PORT)")
    parser.add_argument("--env",default=False,action="store_true",help="Use environment variables (cli options override)")
    parser.add_argument("--verbose",default=False,action="store_true",help="Lots of status messages")
    args=parser.parse_args()

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
    
    while(True):
        time.sleep(0.1)
        if(not(rx_queue.empty())):
            with rx_lock:
                rx=rx_queue.get()
                f=open("rx.json","a")
                f.write(json.dumps(rx))
                f.write("\n")
                f.close()
                if(rx['type']=="RX.DIRECTED"):
                    print("FROM:   ",rx['params']['FROM'])
                    print("TO:     ",rx['params']['TO'])
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

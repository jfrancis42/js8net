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

    start_net(js8host,js8port)
    time.sleep(1)
    print("Call: ",get_callsign())
    print("Grid: ",get_grid())
    print("Info: ",get_info())
    print("Freq: ",get_freq())
    print("Speed: ",get_speed())
    print("Freq: ",set_freq(7078000,2000))
    get_band_activity()
    
    while(True):
        if(not(rx_queue.empty())):
            with rx_lock:
                rx=rx_queue.get()
                if(rx['type']=="RX.DIRECTED"):
                    print(json.dumps(rx,indent=2,sort_keys=True))
            time.sleep(0.1)

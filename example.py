#!/usr/bin/env python3
# coding: utf-8

import sys
import time
import argparse
from js8net import *

# Main program.
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description="Send grid square to APRS.")
    parser.add_argument("--js8_host",default="localhost",help="IP/DNS of JS8Call server (default localhost)")
    parser.add_argument("--js8_port",default=2442,help="TCP port of JS8Call server (default 2442)")
    args=parser.parse_args()

    start_net(args.js8_host,args.js8_port)
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

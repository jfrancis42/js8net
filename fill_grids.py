#!/usr/bin/env python3
# coding: utf-8

import time
import json
from js8net import *
import argparse

# Main program.
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description='Test Script')
    parser.add_argument('--js8_host',default=False,help='IP/DNS of JS8Call server (default localhost)')
    parser.add_argument('--js8_port',default=False,help='TCP port of JS8Call server (default 2442)')
    parser.add_argument("--fill_time",default=False,help="How far back to fill in (default 600 seconds)")
    parser.add_argument("--sleep_time",default=False,help="How long to sleep between requests (default 120 seconds)")
    parser.add_argument("--freq_audio",default=False,help="Specify transmit offset freq (hz, ex: 1000)")
    args=parser.parse_args()

    js8host=False
    js8port=False

    if(args.js8_host):
        js8host=args.js8_host
    else:
        js8host='localhost'

    if(args.js8_port):
        js8port=int(args.js8_port)
    else:
        js8port=2442

    if(args.fill_time):
        filltime=int(args.fill_time)
    else:
        filltime=600

    if(args.sleep_time):
        sleeptime=int(args.sleep_time)
    else:
        sleeptime=120

    flag=False
    start_net(js8host,js8port)
    print("Connected.")
    
    if(args.freq_audio):
        f=get_freq()
        print(f)
        set_freq(f['dial'],int(args.freq_audio))

    stuff=get_call_activity()

    print("Missing grids:")
    for s in stuff:
        if(not(s.grid) and s.age()<=filltime):
            print(s.call)
    print("")

    for s in stuff:
        if(not(s.grid) and s.age()<=filltime):
            print("Requesting grid from "+s.call)
            query_grid(s.call)
            time.sleep(sleeptime)
            flag=True

    if(flag):
        time.sleep(3)

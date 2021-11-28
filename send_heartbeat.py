#!/usr/bin/env python3
# coding: utf-8

import sys
import time
import argparse
from js8net import *

# Main program.
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Send JS8Call Heartbeat.")
    parser.add_argument("--js8_host",default="localhost",help="IP/DNS of JS8Call server (default localhost)")
    parser.add_argument("--js8_port",default=2442,help="TCP port of JS8Call server (default 2442)")
    parser.add_argument("--grid",default=False,help="Override configured grid square")
    parser.add_argument("--freq",default=False,help="Specify transmit freq (hz, ex: 7079000)")
    parser.add_argument("--freq_dial",default=False,help="Specify dial freq (hz, ex: 7078000)")
    parser.add_argument("--freq_audio",default=False,help="Specify transmit offset freq (hz, ex: 1000)")
    args=parser.parse_args()

    start_net(args.js8_host,args.js8_port)
    time.sleep(1)
    if(args.freq or args.freq_dial or args.freq_audio):
        f=get_freq()
        if(args.dial_freq and args.freq_audio):
            set_freq(args.dial_freq,args.freq_audio)
        elif(args.freq and args.freq_audio):
            set_freq(args.freq_dial-args.freq_audio,args.freq_audio)
        elif(args.freq):
            set_freq(args.freq_dial-1000,1000)
        elif(args.freq_audio):
            set_freq(f['dial'],args.freq_audio)
    grid=False
    if(args.grid):
        grid=args.grid
    else:
        grid=get_grid()
    send_heartbeat(grid)
    time.sleep(3)
    print("Message sent.")

#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import time
import argparse
from js8net import *

#
# pip3 install gpsd-py3
#

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
#
# The following functions were taken (and cleaned up and modified for
# python3) from functions originally written by:
#
# René P.F Kanters, Ph.D.
# Director of Computer Assisted Science Education
# Department of Chemistry
# University of Richmond, Virginia 23173
# Phone: (804) 287-6873
# Fax: (804) 287-1897
# Email: rkanters@richmond.edu
# Web: http://www.richmond.edu/~rkanters

def ll2mh(lat,lon,len):
    maxn=len/2
    A=ord('A')
    if(-180<=lon<180):
        pass
    else:
        sys.stderr.write('longitude must be -180<=lon<180\n')
        sys.exit(32)
    if(-90<=lat<90):
        pass
    else:
        sys.stderr.write('latitude must be -90<=lat<90\n')
        sys.exit(33) # can't handle north pole, sorry, [A-R]
    lon=(lon+180.0)/20 # scale down and set up for first digit
    lat=(lat+90.0)/10
    astring=""
    i=0
    while(i<maxn):
        i+=1
        loni=int(lon)
        lati=int(lat)
        if i%2:
            astring+=chr(A+loni)+chr(A+lati)
            lon=(lon-loni)*10
            lat=(lat-lati)*10
        else:
            astring+=str(loni)+str(lati)
            lon=(lon-loni)*24
            lat=(lat-lati)*24
    return(astring)

def c2v(c):
    A=ord('A')
    Zero=ord('0')
    c=ord(c.upper())
    if(c>=A):
        v=c-A
    else:
        v=c-Zero
    return(v)

def mh2ll(mh):
    lon=lat=-90.0
    i=0
    res=10.0    # the initial resolution of the grid in degrees
    npair=len(mh)/2
    while i<npair:
        lon += res*c2v(mh[2*i])
        lat += res*c2v(mh[2*i+1])
        # calculate the alternating 10,24 resolution increment for the next
        # grid level, i.e., 10,24,10,24, etc.
        if i%2: # calculate the resolution for the next subgrid
            res /= 24.0
        else:
            res /= 10.0
        i += 1
    lon*=2
    return([lat,lon])
#
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# Main program.
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Send grid square to APRS.")
    parser.add_argument("--js8_host",default=False,help="IP/DNS of JS8Call server (default localhost, env: JS8HOST)")
    parser.add_argument("--js8_port",default=False,help="TCP port of JS8Call server (default 2442, env: JS8PORT)")
    parser.add_argument("--gpsd_host",default=False,help="IP/DNS of GPSD host (default localhost, env: GPSDHOST)")
    parser.add_argument("--gpsd_port",default=False,help="TCP port of GPSD host (default 2947, env: GPSDPORT)")
    parser.add_argument("--set_grid",default=False,action="store_true",help="Set the JS8Call grid square")
    parser.add_argument("--get_grid",default=False,action="store_true",help="Use the pre-configured JS8Call grid square")
    parser.add_argument("--grid_digits",default=10,help="How many grid square digits to store in JS8Call (default 10)")
    parser.add_argument("--track",default=False,help="Track")
    parser.add_argument("--interval",default=600,help="Seconds between track location transmissions (default 600)")
    parser.add_argument("--lat",default=False,help="Specify latitude")
    parser.add_argument("--lon",default=False,help="Specify longitude")
    parser.add_argument("--grid",default=False,help="Specify grid square")
    parser.add_argument("--freq",default=False,help="Specify transmit freq (hz, ex: 7079000)")
    parser.add_argument("--freq_dial",default=False,help="Specify dial freq (hz, ex: 7078000)")
    parser.add_argument("--freq_audio",default=False,help="Specify transmit offset freq (hz, ex: 1000)")
    parser.add_argument("--speed",default=False,help="Specify transmit speed (slow==4, normal==0, fast==1, turbo==2)")
    parser.add_argument("--fake_send",default=False,action="store_true",help="Don't actually send")
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
        js8port=int(args.js8_port)
    elif(os.environ.get("JS8PORT") and args.env):
        js8port=int(os.environ.get("JS8PORT"))
    else:
        js8port=2442

    gpsdhost=False
    gpsdport=False

    if(args.gpsd_host):
        gpsdhost=args.gpsd_host
    elif(os.environ.get("GPSDHOST") and args.env):
        gpsdhost=os.environ.get("GPSDHOST")
    else:
        gpsdhost="localhost"

    if(args.gpsd_port):
        gpsdport=int(args.gpsd_port)
    elif(os.environ.get("GPSDPORT") and args.env):
        gpsdport=int(os.environ.get("GPSDPORT"))
    else:
        gpsdport=2947

    if(args.gpsd_host or (args.env and (os.environ.get("GPSDHOST") or os.environ.get("GPSDPORT")))):
        import gpsd

    if(args.verbose):
        print("Connecting to JS8Call...")
    start_net(js8host,js8port)
    if(args.verbose):
        print("Connected.")
    grid=False
    if(args.freq or args.freq_dial or args.freq_audio):
        f=get_freq()
        if(args.freq_dial and args.freq_audio):
            set_freq(args.freq_dial,args.freq_audio)
        elif(args.freq and args.freq_audio):
            set_freq(args.freq_dial-args.freq_audio,args.freq_audio)
        elif(args.freq):
            set_freq(args.freq_dial-1000,1000)
        elif(args.freq_audio):
            set_freq(f['dial'],args.freq_audio)
    if(args.verbose):
        print("Frequency set to ",get_freq())
    if(args.speed):
        speed=int(args.speed)
        if(speed>=0 and speed<=4 and speed!=3):
            if(args.verbose):
                print("Setting speed to ",str(speed))
            set_speed(speed)
    if(args.get_grid):
        grid=get_grid()
    if(args.lat and args.lon):
        grid=ll2mh(float(args.lat),float(args.lon),int(args.grid_digits))
    if(args.grid):
        grid=args.grid
    if(args.gpsd_host or (args.env and (os.environ.get("GPSDHOST") or os.environ.get("GPSDPORT")))):
        if(args.verbose):
            print("Connecting to GPSD...")
        gpsd.connect(host=gpsdhost,port=gpsdport)
        if(args.verbose):
            print("Connected.")
        if(args.verbose):
            print("Complete.")
        packet=gpsd.get_current()
        grid=ll2mh(packet.lat,packet.lon,int(args.grid_digits))
    if(grid):
        if(args.set_grid):
            set_grid(grid)
        if(not(args.fake_send)):
            if(args.track):
                while(True):
                    packet=gpsd.get_current()
                    grid=ll2mh(packet.lat,packet.lon,int(args.grid_digits))
                    send_aprs_grid(grid)
                    if(args.verbose):
                        print("Sent grid: ",grid)
                        print("lat/lon: ",mh2ll(grid))
                    time.sleep(int(args.interval))
            else:
#                packet=gpsd.get_current()
#                grid=ll2mh(packet.lat,packet.lon,int(args.grid_digits))
                send_aprs_grid(grid)
                if(args.verbose):
                    print("Sent grid: ",grid)
                    print("lat/lon: ",mh2ll(grid))
        if(not(args.fake_send)):
            time.sleep(3)
    else:
        print("No grid specified, no data sent.")

#!/usr/bin/env python3
# coding: utf-8

import sys
import time
import argparse
from js8net import *

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
    parser.add_argument("--js8_host",default="localhost",help="IP/DNS of JS8Call server (default localhost)")
    parser.add_argument("--js8_port",default=2442,help="TCP port of JS8Call server (default 2442)")
    parser.add_argument("--setgrid",default=False,action="store_true",help="Set the JS8Call grid square")
    parser.add_argument("--getgrid",default=False,action="store_true",help="Use the pre-configured JS8Call grid square")
    parser.add_argument("--grid_digits",default=6,help="How many grid square digits to store in JS8Call (default 6)")
    parser.add_argument("--lat",default=False,help="Specify latitude")
    parser.add_argument("--lon",default=False,help="Specify longitude")
    parser.add_argument("--grid",default=False,help="Specify grid square")
    args=parser.parse_args()

    start_net(args.js8_host,args.js8_port)
    time.sleep(1)
    grid=False
    if(args.getgrid):
        grid=get_grid()
    if(args.lat and args.lon):
        grid=ll2mh(args.lat,args.lon,args.grid_digits)
    if(args.grid):
        grid=args.grid
    if(grid):
        if(args.setgrid):
            set_grid(grid)
        send_aprs_grid(grid)
        print("Sent grid: ",grid)
        print("lat/lon: ",mh2ll(grid))
    else:
        print("No grid specified, no data sent.")

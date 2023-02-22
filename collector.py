#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import time
import json
import argparse
import maidenhead as mh
from js8net import *
#import pdb
import requests
import uuid
import json
import re

global js8host
global js8port
global mycall
global mygrid
global myfreq
global myspeed
global myuuid
global radio
global aggregator

global station_lock
global cmd_queue
global cmd_lock
station_lock=threading.Lock()
cmd_queue=Queue()
cmd_lock=threading.Lock()

global tx_allowed
tx_allowed=False

def update_thread(name):
    global js8host
    global js8port
    global mycall
    global mygrid
    global myfreq
    global myspeed
    global myuuid
    print(name+' started...')
    last=time.time()
    while(True):
        with station_lock:
            mycall=get_callsign()
            mygrid=get_grid()
            myfreq=get_freq()
            myspeed=get_speed()
        if(time.time()>=last+30):
            last=time.time()
            act=get_call_activity()
            if(act):
                stuff=[]
                for a in act:
                    stuff.append({'call':a.call,'snr':a.snr,'utc':a.utc,'grid':a.grid})
                res=requests.post('http://'+aggregator+'/collect',json={'type':'grids','uuid':myuuid,'stuff':stuff})
                print(res)
                res.close()
        time.sleep(5.0)

def traffic_thread(name):
    global aggregator
    global myuuid
    print(name+' started...')
    while(True):
        time.sleep(0.1)
        if(not(rx_queue.empty())):
            with rx_lock:
                rx=rx_queue.get()
            print('New traffic received...')
            if(rx['type']=='RX.DIRECTED'):
                print('Sending traffic to aggregator...')
                print(rx)
                rx['uuid']=myuuid
                res=requests.post('http://'+aggregator+'/collect',json={'type':'traffic','stuff':rx})
                print(res)
                res.close()
            else:
                print('Not sending traffic to aggregator...')
                print(rx)

def station_thread(name):
    global aggregator
    global myuuid
    global mycall
    global mygrid
    global js8host
    global js8port
    global myspeed
    global myfreq
    global radio
    global tx_allowed
    print(name+' started...')
    time.sleep(7.5)
    while(True):
        with station_lock:
            if(mygrid and mygrid!=''):
                if(len(mygrid)>8):
                    (lat,lon)=mh.to_location(mygrid[0:8])
                else:
                    (lat,lon)=mh.to_location(mygrid)
            else:
                lat=False
                lon=False
            j={'time': time.time(),
               'en_time': time.asctime(),
               'call': mycall,
               'grid': mygrid,
               'lat': lat,
               'lon': lon,
               'host': js8host,
               'port': js8port,
               'speed': myspeed,
               'dial': myfreq['dial'],
               'carrier': myfreq['offset'],
               'radio': radio,
               'tx':tx_allowed}
            res=requests.post('http://'+aggregator+'/collect',json={'type':'station','uuid':myuuid,'stuff':j})
            print('sending station')
            print(res)
#            j=res.json() # these are basically placeholders for sending commands back to the radios
#            print(j)
            res.close()
        time.sleep(15)
                        
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# Main program.
if(__name__ == '__main__'):
    parser=argparse.ArgumentParser(description='JS8call data collector.')
    parser.add_argument('--js8_host',default=False,help='IP/DNS of JS8Call server (default localhost)')
    parser.add_argument('--js8_port',default=False,help='TCP port of JS8Call server (default 2442)')
    parser.add_argument('--aggregator',default=False,help='Aggregator to send traffic to (default is localhost:8000)')
    parser.add_argument('--uuid',default=False,help='Use a specific UUID (default is auto-generate)')
    parser.add_argument('--radio',default=False,help='Type/model of radio (used for display only)')
    parser.add_argument('--transmit',default=False,help='This station allowed to transmit (default is rx only)',
                        action='store_true')
    args=parser.parse_args()

    js8host=False
    js8port=False

    mycall='unknown'
    mygrid='unknown'
    myfreq={'dial': 0, 'freq': 0, 'offset': 0}
    myspeed='0'
    
    tx_allowed=args.transmit

    if(args.js8_host):
        js8host=args.js8_host
    else:
        js8host='localhost'

    if(args.js8_port):
        js8port=int(args.js8_port)
    else:
        js8port=2442

    if(args.aggregator):
        aggregator=args.aggregator
    else:
        aggregator='localhost:8000'

    if(args.radio):
        radio=args.radio
    else:
        radio='unknown'

    if(args.uuid):
        myuuid=args.uuid
    else:
        myuuid=str(uuid.uuid4())

    print('Connecting to JS8Call...')
    start_net(js8host,js8port)
    print('Connected.')

    thread0=Thread(target=update_thread,args=('Update Thread',),daemon=True)
    thread0.start()
    thread1=Thread(target=traffic_thread,args=('Traffic Thread',),daemon=True)
    thread1.start()
    thread2=Thread(target=station_thread,args=('Station Thread',),daemon=True)
    thread2.start()
    
    while(True):
        if(not(thread0.is_alive())):
            print('(re-)starting Update Thread...')
            thread0.join()
            thread0=Thread(target=update_thread,args=('Update Thread',),daemon=True)
            thread0.start()
        if(not(thread1.is_alive())):
            print('(re-)starting Traffic Thread...')
            thread1.join()
            thread1=Thread(target=traffic_thread,args=('Traffic Thread',),daemon=True)
            thread1.start()
        if(not(thread2.is_alive())):
            print('(re-)starting Station Thread...')
            thread2.join()
            thread2=Thread(target=station_thread,args=('Station Thread',),daemon=True)
            thread2.start()
        time.sleep(1.0)

#    pdb.set_trace()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

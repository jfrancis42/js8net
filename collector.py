#!/usr/bin/env python3
# coding: utf-8

global version
version='0.1'

import os
import sys
import time
import json
import argparse
from js8net import *
#import pdb
import requests
import uuid
import json

global js8host
global js8port
global mycall
global mygrid
global myfreq
global myspeed
global myuuid
global radio
global peer

global station_lock
station_lock=threading.Lock()

def update_thread(name):
    global js8host
    global js8port
    global mycall
    global mygrid
    global myfreq
    global myspeed
    while(True):
        with station_lock:
            mycall=get_callsign()
            mygrid=get_grid()
            myfreq=get_freq()
            myspeed=get_speed()
            time.sleep(5.0)

def traffic_thread(name):
    global peer
    global myuuid
    global version
    print(name+' started...')
    while(True):
        time.sleep(0.1)
        if(not(rx_queue.empty())):
            with rx_lock:
                rx=rx_queue.get()
            print('New traffic received...')
            if(rx['type']=='RX.DIRECTED' or rx['type']=='RX.ACTIVITY'):
                print('Sending traffic to peer...')
                rx['uuid']=myuuid
                rx['version']=version
                print(rx)
                res=requests.post('http://'+peer+'/traffic',json={'traffic':rx})
                print(res)
                res.close()
                        
def station_thread(name):
    global peer
    global myuuid
    global mycall
    global mygrid
    global js8host
    global js8port
    global myspeed
    global myfreq
    global radio
    global version
    print(name+' started...')
    time.sleep(7.5)
    olddial=False
    oldcarrier=False
    oldspeed=False
    lasttime=0
    while(True):
        with station_lock:
            now=time.time()
            if(olddial!=myfreq['dial'] or
               oldcarrier!=myfreq['offset'] or
               oldspeed!=myspeed or
               now-lasttime>90):
                olddial=myfreq['dial']
                oldcarrier=myfreq['offset']
                oldspeed=myspeed
                lasttime=now
                j={'time': now,
                   'en_time': time.asctime(),
                   'call': mycall,
                   'grid': mygrid,
                   'host': js8host,
                   'port': js8port,
                   'speed': myspeed,
                   'dial': myfreq['dial'],
                   'carrier': myfreq['offset'],
                   'uuid': myuuid,
                   'radio': radio,
                   'version': version}
                print(j)
                res=requests.post('http://'+peer+'/station',json={'station':j})
                print(res)
                res.close()
        time.sleep(1)
                        
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# Main program.
if(__name__ == '__main__'):
    parser=argparse.ArgumentParser(description='Send JS8Call Heartbeat.')
    parser.add_argument('--js8_host',default=False,help='IP/DNS of JS8Call server (default localhost)')
    parser.add_argument('--js8_port',default=False,help='TCP port of JS8Call server (default 2442)')
    parser.add_argument('--peer',default=False,help='Peer to send traffic to (default is localhost:8001)')
    parser.add_argument('--uuid',default=False,help='Use a specific UUID (default is auto-generate)')
    parser.add_argument('--radio',default=False,help='Type/model of radio (for display only)')
    args=parser.parse_args()

    js8host=False
    js8port=False

    mycall='unknown'
    mygrid='unknown'
    myfreq={'dial': 0, 'freq': 0, 'offset': 0}
    myspeed='0'
    
    if(args.js8_host):
        js8host=args.js8_host
    else:
        js8host='localhost'

    if(args.js8_port):
        js8port=int(args.js8_port)
    else:
        js8port=2442

    if(args.peer):
        peer=args.peer
    else:
        peer='localhost:8001'

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
        # TODO: Maybe do some screen update stuff here at some point,
        # but for now, just let the threads roll...
        time.sleep(1.0)

#    pdb.set_trace()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

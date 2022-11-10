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
    print(name+' started...')
    while(True):
        with station_lock:
            mycall=get_callsign()
            mygrid=get_grid()
            myfreq=get_freq()
            myspeed=get_speed()
        time.sleep(5.0)

def traffic_thread(name):
    global aggregator
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
                print('Sending traffic to aggregator...')
                rx['uuid']=myuuid
                rx['version']=version
                print(rx)
                res=requests.post('http://'+aggregator+'/traffic',json={'traffic':rx})
                print(res)
                res.close()
                        
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
    global version
    global tx_allowed
    print(name+' started...')
    time.sleep(7.5)
    while(True):
        with station_lock:
            j={'time': time.time(),
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
               'tx':tx_allowed,
               'version': version}
            print(j)
            res=requests.post('http://'+aggregator+'/station',json={'station':j})
            print(res)
            j=res.json()
            print(j)
            res.close()
        if('cmd' in j):
            print('Command: '+str(j))
            if(j['cmd']):
                if('uuid' in j):
                    if(j['uuid']==myuuid):
                        print('Received a valid command: '+j['cmd'])
                        if(j['cmd']=='send-grid'):
                            if('grid' in j):
                                if(tx_allowed):
                                    send_aprs_grid(j['grid'])
                            else:
                                if(tx_allowed):
                                    send_aprs_grid(get_grid())
                        elif(j['cmd']=='send-hb'):
                            if(tx_allowed):
                                send_heartbeat()
                        elif(j['cmd']=='send-text'):
                            if(tx_allowed):
                                content=j['content']
                                if(len(content)>67):
                                    content=content[0:67]
                                send_sms(re.sub('\D','',j['phone']),content)
                        elif(j['cmd']=='send-aprs'):
                            if(tx_allowed):
                                content=j['content']
                                if(len(content)>67):
                                    content=content[0:67]
                                send_aprs(j['aprs-call'],content)
                        elif(j['cmd']=='send-email'):
                            if(tx_allowed):
                                content=j['content']
                                if(len(content)>67):
                                    content=content[0:67]
                                send_email(j['addr'],content)
                    else:
                        print('Command received, but not for me...')
        else:
            print('No valid command received')
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
        # TODO: Maybe do some screen update stuff here at some point,
        # but for now, just let the threads roll...
        time.sleep(1.0)

#    pdb.set_trace()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

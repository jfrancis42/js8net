#!/usr/bin/env python3
# coding: utf-8

global version
version='0.1'

import os
import sys
import time
import json
import argparse
#import pdb
import requests
import json
import uuid
import csv
from os.path import exists
import threading
from threading import Thread
from yattag import Doc
import maidenhead as mh

from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

global max_age
global listen

global traffic
global traffic_lock
traffic=[]
traffic_lock=threading.Lock()
global stations
global stations_lock
stations={}
stations_lock=threading.Lock()
global grids
grids={}

global eom
global error
eom="♢"
error="…"

def main_page ():
    doc, tag, text=Doc().tagtext()
    with tag('html', lang='en'):
        with tag('body'):
            with tag('div', id='wrapper'):
                text('JS8Call Aggregator')
    return(doc.getvalue())

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        doc, tag, text=Doc().tagtext()
        global traffic
        global traffic_lock
        global stations
        global stations_lock
        global version
        if(self.path=='/'):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str.encode(main_page()))
        if(self.path=='/fetch'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            with traffic_lock:
                with stations_lock:
                    j={'version':version,
                       'stations':stations,
                       'traffic':traffic}
            self.wfile.write(str.encode(json.dumps(j)))

    def do_POST(self):
        global traffic
        global traffic_lock
        global stations
        global stations_lock
        global listen
        global error
        content_length=int(self.headers['Content-Length'])
        payload=self.rfile.read(content_length).decode('utf8')
        j=json.loads(payload)
        print('payload: '+payload)
        if(self.path=='/traffic'):
            self.send_response(200)
            self.end_headers()
            if('traffic' in j):
                if('uuid' in j['traffic']):
                    print('Traffic from '+j['traffic']['uuid'])
                    rx=j['traffic']
                    if('FROM' in rx['params'] and 'GRID' in rx['params']): # don't sub a less accurate grid
                        if(rx['params']['GRID']!=''):
                            if(rx['params']['FROM'] in grids):
                                if(rx['params']['GRID'] in grids):
                                    pass
                                else:
                                    grids[rx['params']['FROM']]=rx['params']['GRID']
                            else:
                                grids[rx['params']['FROM']]=rx['params']['GRID']
                        elif(rx['params']['FROM'] in grids):
                            rx['params']['GRID']=grids[rx['params']['FROM']]
                    if('FROM' in rx['params'] and 'TEXT' in rx['params']):
                        tmp=rx['params']['TEXT'].split()
                        if(len(tmp)>3):
                            if(tmp[2]=='GRID'):
                                if(error in tmp[3]):
                                    pass
                                else:
                                    grids[rx['params']['FROM']]=tmp[3]
                    with traffic_lock:
                        traffic.append(rx)
        if(self.path=='/station'):
            self.send_response(200)
            self.end_headers()
            if('station' in j):
                if('uuid' in j['station']):
                    print('Station info from '+j['station']['uuid'])
                    with stations_lock:
                        if('grid' in j['station']):
                            if(j['station']['grid']!=''):
                                if(len(j['station']['grid'])>8):
                                    (lat,lon)=mh.to_location(j['station']['grid'][0:8])
                                else:
                                    (lat,lon)=mh.to_location(j['station']['grid'])
                                j['station']['lat']=lat
                                j['station']['lon']=lon
                        stations[j['station']['uuid']]=j['station']

def housekeeping_thread(name):
    global traffic
    global traffic_lock
    global stations
    global stations_lock
    global max_age
    while(True):
        time.sleep(31)
        now=time.time()
        with traffic_lock:
            traffic=list(filter(lambda n: n['time'] > now-max_age,traffic))
            f=open('/tmp/xtraffic.json','w')
            f.write(json.dumps(traffic))
            f.write('\n')
            f.close()
        with stations_lock:
            for u in list(stations.keys()):
                if(stations[u]['time'] < now-max_age):
                    del(stations[u])
            f=open('/tmp/stations.json','w')
            f.write(json.dumps(stations))
            f.write('\n')
            f.close()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# Main program.
if(__name__ == '__main__'):
    parser=argparse.ArgumentParser(description='Send JS8Call info.')
    parser.add_argument('--listen',default=False,help='Listen to peer traffic (default 8001)')
    parser.add_argument('--max_age',default=False,help='Maximum traffic age (default 3600 seconds)')
    parser.add_argument('--localhost',default=False,help='Bind to localhost only (default 0.0.0.0)')
    args=parser.parse_args()

    if(args.listen):
        listen=int(args.listen)
    else:
        listen=8001
    print('Listening on port: '+str(listen))

    if(args.max_age):
        max_age=int(args.max_age)
    else:
        max_age=3600
    print('Max age: '+str(max_age))

    if(args.localhost):
        localhost=True
    else:
        localhost=False

    if(exists('/tmp/xtraffic.json')):
        with traffic_lock:
            f=open('/tmp/xtraffic.json')
            traffic=json.load(f)
            f.close()

    if(exists('/tmp/stations.json')):
        with stations_lock:
            f=open('/tmp/stations.json')
            stations=json.load(f)
            f.close()
    
    thread0=Thread(target=housekeeping_thread,args=('Housekeeping Thread',),daemon=True)
    thread0.start()
    
    if(localhost):
        httpd=HTTPServer(('127.0.0.1', listen), SimpleHTTPRequestHandler)
    else:
        httpd=HTTPServer(('0.0.0.0', listen), SimpleHTTPRequestHandler)
    httpd.serve_forever()
#    pdb.set_trace()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

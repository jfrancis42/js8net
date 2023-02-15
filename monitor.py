#!/usr/bin/env python3
# coding: utf-8

global version
version='0.2'

#import pdb
import os
import sys
import time
import json
import argparse
import requests
import uuid
import csv
from os.path import exists
from os.path import expanduser
from os import mkdir
import threading
from threading import Thread
from yattag import Doc
import maidenhead as mh
from queue import Queue
from urllib.parse import urlparse,parse_qs
from http.server import HTTPServer,BaseHTTPRequestHandler
import urllib
from io import BytesIO
import datetime
from js8net import *
import pyproj
import dbm

global max_age
global listen
global basedir

global traffic
global traffic_lock
traffic=[]
traffic_lock=threading.Lock()

global stations
global stations_lock
stations={}
stations_lock=threading.Lock()

global grids
global grids_lock
grids={}
grids_lock=threading.Lock()

global id
id=False

global eom
global error
eom="♢"
error="…"

global css
global colors

colors={}
colors['friend']='#F1C40F'
colors['mycall']='#2ECC71'
colors['at']='#5DADE2'
colors['snr_supergreen']='#66FF00'
colors['snr_green']='#7CD342'
colors['snr_yellow']='#FDD835'
colors['snr_red']='#F4511E'
colors['heartbeat']='#FADBD8'
colors['query']='#D6EAF8'
colors['table_header_background']='#08389F'
colors['table_header_text']='#FFFFFF'
colors['link']='#000000'
colors['border_bottom_odd']='#DDDDDD'
colors['border_bottom_even']='#F3F3F3'
colors['border_bottom_last']='#009879'
colors['cq']='#FCF3CF'
colors['non_zombie_traffic']='#FFFFFF'
colors['close']='#D4EFDF'

css=''
css+='a {'
css+='  color: '+colors['link']+';'
css+='  text-decoration: none;'
css+='  text-transform: uppercase;'
css+='}'
css+='.styled-table {'
css+='    border-collapse: collapse;'
css+='    margin: 25px 0;'
css+='    font-size: 0.9em;'
css+='    font-family: sans-serif;'
css+='    min-width: 400px;'
css+='    box-shadow: 0 0 20px rgba(0,0,0,0.5);'
css+='}'
css+='.embedded-table {'
css+='    border-collapse: collapse;'
css+='    margin: 25px 0;'
css+='    font-size: 0.9em;'
css+='    font-family: sans-serif;'
css+='}'
css+='.styled-table thead tr {'
css+='    background-color: '+colors['table_header_background']+';'
css+='    color: '+colors['table_header_text']+';'
css+='    text-align: left;'
css+='}'
css+='.styled-table th,'
css+='.styled-table td {'
css+='    padding: 12px 15px;'
css+='}'
css+='.styled-table tbody tr {'
css+='    border-bottom: 1px solid '+colors['border_bottom_odd']+';'
css+='}'
css+='.styled-table tbody tr:nth-of-type(even) {'
css+='    background-color: '+colors['border_bottom_even']+';'
css+='}'
css+='.styled-table tbody tr:last-of-type {'
css+='    border-bottom: 2px solid '+colors['border_bottom_last']+';'
css+='}'
css+='* {';
css+='    margin: 0;';
css+='    padding: 0;';
css+='}';
css+='.imgbox {';
css+='    display: grid;';
css+='    height: 100%;';
css+='}';
css+='.center-fit {';
css+='    max-width: 100%;';
css+='    max-height: 100vh;';
css+='    margin: auto;';
css+='}';
css+='.tooltip {';
css+='  position: relative;';
css+='  display: inline-block;';
css+='  border-bottom: 1px dotted black;';
css+='}';
css+='.tooltip .tooltiptext {';
css+='  visibility: hidden;';
css+='  width: 500px;';
css+='  background-color: black;';
css+='  color: #fff;';
css+='  text-align: center;';
css+='  border-radius: 6px;';
css+='  padding: 5px 0;';
css+='  /* Position the tooltip */';
css+='  position: absolute;';
css+='  z-index: 1;';
css+='  top: -5px;';
css+='  left: 105%;';
css+='}';
css+='.tooltip:hover .tooltiptext {';
css+='  visibility: visible;';
css+='}';

def housekeeping_thread(name):
    global traffic
    global traffic_lock
    global stations
    global stations_lock
    global grids
    global grids_lock
    global max_age
    print(name+' started...')
    while(True):
        time.sleep(60.0)
        print('-----------------------------------------')
        print('Keeping house...')
        now=time.time()
        with grids_lock:
            with stations_lock:
                with traffic_lock:
                     for call in grids.keys():
                        g=json.loads(grids[call])
                        if(g['utc']<now-max_age):
                            del(grids[call])
                        for uuid in stations.keys():
                            s=json.loads(stations[uuid])
                            if(s['stuff']['time']<now-max_age):
                                del(stations[uuid])
                        for key in traffic.keys():
                            ts=float(key)
                            if(ts<now-max_age):
                                del(traffic[key])
        print('Done.')
        print('-----------------------------------------')

def main_page ():
    global css
    global basedir
    doc,tag,text=Doc().tagtext()
    with tag('html',lang='en'):
        with tag('head'):
            with tag('style'):
                text(css)
        with tag('body'):
            with open(basedir+'monitor.js','r') as file:
                js=file.read()
            with tag('script',type='text/javascript'):
                doc.asis(js)
            with tag('div',id='wrapper'):
#                with tag('h1'):
#                    text('Connections')
#                with tag('table',id='connections',klass='styled-table'):
#                    pass
#                    with tag('tr'):
#                        with tag('td'):
#                            text('foo')
#                            with tag('div',klass='imgbox'):
#                                with tag('img',id='c-img',klass='center-fit',src='/connections/'+str(time.time())+'.jpg'):
#                                    pass
#                with tag('br'):
#                    pass
                with tag('h1'):
                    text('Stations')
                with tag('table',id='stations',klass='styled-table'):
                    pass
                with tag('br'):
                    pass
                with tag('h1'):
                    text('Traffic')
                with tag('table',id='traffic',klass='styled-table'):
                    pass
                with tag('br'):
                    pass
                with tag('a',href='https://github.com/jfrancis42/js8net',target='_blank'):
                    text('js8net')
                text(' by ')
                with tag('a',href='https://www.qrz.com/db/N0GQ',target='_blank'):
                    text('N0GQ')
                with tag('br'):
                    pass
    return(doc.getvalue())

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global traffic
        global traffic_lock
        global stations
        global stations_lock
        global grids
        global grids_lock
        global colors
        doc,tag,text=Doc().tagtext()
        if(self.path=='/'):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str.encode(main_page()))
        if(self.path=='/colors'):
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            if(exists('colors.dat')):
                print('Loading colors...')
                with open(basedir+'colors.dat','r',encoding='utf8') as colors_file:
                    colors_reader=csv.reader(colors_file,delimiter=',')
                    for row in colors_reader:
                        colors[row[0]]=row[1]
            self.wfile.write(str.encode(json.dumps(colors)))
        if(self.path.find('/svg/')==0):
            tmp=self.path.split('/')
            if(len(tmp)!=3):
                print('Bad svg request: '+self.path)
                self.send_response(404)
                self.end_headers()
            else:                
                image=tmp[2]
                print('Requested svg: '+image)
                if(exists('images/'+image)):
                    self.send_response(200)
                    self.send_header('Content-type','image/svg+xml')
                    self.end_headers()
                    with open(basedir+'images/'+image,'r') as file:
                        img=file.read()
                    self.wfile.write(str.encode(img))
                else:
                    self.send_response(404)
                    self.end_headers()
        if(self.path=='/json'):
            with grids_lock:
                with stations_lock:
                    with traffic_lock:
                        self.send_response(200)
                        self.send_header('Content-type','application/json')
                        self.end_headers()
                        out={}
                        out['grids']={}
                        for call in grids.keys():
                            g=json.loads(grids[call])
                            out['grids'][call.decode('utf-8').split('/')[0]]=g
                        out['stations']={}
                        for uuid in stations.keys():
                            s=json.loads(stations[uuid])
                            out['stations'][uuid.decode('utf-8')]=s
                        out['traffic']=[]
                        for key in traffic.keys():
                            k=json.loads(traffic[key])
#                            out['traffic'][key.decode('utf-8')]=k
                            if(k['stuff']['type']=='RX.DIRECTED'):
                                out['traffic'].append(k)
                        self.wfile.write(str.encode(json.dumps(out)))

    def do_POST(self):
        global traffic
        global traffic_lock
        global stations
        global stations_lock
        global listen
        global error
        global commands
        global grids
        global max_age
        global id
        content_length=int(self.headers['Content-Length'])
        payload=self.rfile.read(content_length).decode('utf8')
        if(self.path=='/collect'):
            j=json.loads(payload)
            self.send_response(200)
            self.end_headers()
            print('payload: '+payload)
            print('type: '+j['type'])
            now=time.time()
            if(j['type']=='grids'):
                with grids_lock:
                    for g in j['stuff']:
                        if(g['utc']>now-max_age):
                            g['uuid']=j['uuid']
                            call=g['call']
                            del(g['call'])
                            grids[call]=json.dumps(g)
            if(j['type']=='station'):
                with stations_lock:
                    stations[j['uuid']]=json.dumps(j)
            if(j['type']=='traffic'):
                with traffic_lock:
                    # Set the from call, if available.
                    if('FROM' in j['stuff']['params']):
                        fmcall=j['stuff']['params']['FROM'].split('/')[0]
                        j['from_call']=fmcall
                    else:
                        j['from_call']=False
                        fmcall=False
                    # Set the to call, if available. Also flag if it's to an "at".
                    if('TO' in j['stuff']['params']):
                        tocall=j['stuff']['params']['TO'].split('/')[0]
                        j['to_call']=tocall
                        if(j['to_call'][0]=='@'):
                            j['to_at']=True
                            toat=True
                        else:
                            j['to_at']=False
                            toat=False
                    else:
                        tocall=False
                        j['to_call']=False
                        j['to_at']=False
                    # Set the from grid, if known.
                    if(fmcall.encode('utf-8') in grids.keys()):
                        fmgrid=json.loads(grids[fmcall])['grid']
                        j['from_grid']=fmgrid
                    else:
                        fmgrid=False
                        j['from_grid']=False
                    # Set the to grid, if known.
                    if(tocall.encode('utf-8') in grids.keys()):
                        togrid=json.loads(grids[tocall])['grid']
                        j['to_grid']=togrid
                    else:
                        togrid=False
                        j['to_grid']=False
                    # ToDo: later
                    j['from_flag']=False
                    j['to_flag']=False
                    j['from_country']=False
                    j['to_country']=False
                    j['from_info']=False
                    j['to_info']=False
                    j['from_addr']=False
                    j['to_addr']=False
                    # SNR
                    j['snr']=j['stuff']['params']['SNR']
                    # Speed
                    j['speed']=j['stuff']['params']['SPEED']
                    # Freq
                    j['freq']=j['stuff']['params']['FREQ']
                    # Text
                    j['text']=j['stuff']['params']['TEXT']
                    # From lat/lon
#                    if(fmgrid):
#                        if(len(fmgrid)>8):
#                            (lat,lon)=mh.to_location(fmgrid[0:8])
#                        else:
#                            (lat,lon)=mh.to_location(fmgrid)
#                        j['from_lat']=lat
#                        j['from_lon']=lon
#                    else:
#                        j['from_lat']=False
#                        j['from_lon']=False
#                    # To lat/lon
#                    if(togrid):
#                        if(len(togrid)>8):
#                            (lat,lon)=mh.to_location(togrid[0:8])
#                        else:
#                            (lat,lon)=mh.to_location(togrid)
#                        j['to_lat']=lat
#                        j['to_lon']=lon
#                    else:
#                        j['to_lat']=False
#                        j['to_lon']=False
                    key=str(j['stuff']['time'])
                    # Todo: later, del(j['stuff'])
                    # Set the ID
                    j['id']=':'.join([fmcall,tocall,key,str(j['freq'])])
                    traffic[key]=json.dumps(j)
                print(json.dumps(j))
        else:
            self.send_response(404)
            self.end_headers()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# Main program.
if(__name__ == '__main__'):
    parser=argparse.ArgumentParser(description='Aggregate collected JS8call data from collectors.')
    parser.add_argument('--listen',default=False,help='Listen port for collector traffic (default 8000)')
    parser.add_argument('--basedir',default=False,help='Monitor program directory (default is ~/.js8net/)')
    parser.add_argument('--max_age',default=False,help='Maximum traffic age (default 3600 seconds)')
    parser.add_argument('--localhost',default=False,help='Bind to localhost only (default 0.0.0.0)',
                        action='store_true')

    args=parser.parse_args()

    if(args.listen):
        listen=int(args.listen)
    else:
        listen=8000
    print('Listening on port: '+str(listen))

    if(args.basedir):
        basedir=args.basedir
        if(basedir[-1]!='/'):
           basedir=basedir+'/'
    else:
        basedir=expanduser("~")+'/.js8net/'
        if(not(exists(basedir))):
            mkdir(basedir)

    if(args.max_age):
        max_age=int(args.max_age)
    else:
        max_age=3600
    print('Max age: '+str(max_age))

    if(args.localhost):
        localhost=True
    else:
        localhost=False

#    pdb.set_trace()
    if(localhost):
        print('Running web server on localhost only...')
        httpd=HTTPServer(('127.0.0.1',listen),SimpleHTTPRequestHandler)
    else:
        print('Running web server on all interfaces...')
        httpd=HTTPServer(('0.0.0.0',listen),SimpleHTTPRequestHandler)

    grids=dbm.open(basedir+'grids.dbm','c')
    stations=dbm.open(basedir+'stations.dbm','c')
    traffic=dbm.open(basedir+'traffic.dbm','c')

    thread0=Thread(target=housekeeping_thread,args=('Housekeeping Thread',),daemon=True)
    thread0.start()

    httpd.serve_forever()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

#!/usr/bin/env python3
# coding: utf-8

#
# pip3 install yattag
#

import os
import sys
import time
import json
import argparse
from os.path import exists
from js8net import *
#import pdb
import csv
import requests

from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from yattag import Doc
import json

global traffic
global traffic_lock
global stations
global calls
global refresh
global mycall
global uuids
global uindex
global max_age

global aggregator
global webport

def main_page ():
    global refresh
    doc, tag, text=Doc().tagtext()
    with tag('html', lang='en'):
        with tag('head'):
            with tag('style'):
                text('.styled-table {')
                text('    border-collapse: collapse;')
                text('    margin: 25px 0;')
                text('    font-size: 0.9em;')
                text('    font-family: sans-serif;')
                text('    min-width: 400px;')
                text('    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);')
                text('}')
                text('.styled-table thead tr {')
                text('    background-color: #689F38;')
                text('    color: #ffffff;')
                text('    text-align: left;')
                text('}')
                text('.styled-table th,')
                text('.styled-table td {')
                text('    padding: 12px 15px;')
                text('}')
                text('.styled-table tbody tr {')
                text('    border-bottom: 1px solid #dddddd;')
                text('}')
                text('.styled-table tbody tr:nth-of-type(even) {')
                text('    background-color: #f3f3f3;')
                text('}')
                text('.styled-table tbody tr:last-of-type {')
                text('    border-bottom: 2px solid #009879;')
                text('}')
                text('.styled-table tbody tr.active-row {')
                text('    font-weight: bold;')
                text('    color: #009879;')
                text('}')
        with tag('body'):
            with tag('script', type='text/javascript'):
                text('\nvar intervalId = setInterval(function() {\n')
                text('  getText(\"/jsstatus\");\n')
                text('  async function getText(file) {\n')
                text('    let myObject = await fetch(file);\n')
                text('    let myText = await myObject.text();\n')
                text('    var obj = JSON.parse(myText);\n')
                text('    document.getElementById(\"traffic\").innerHTML = obj.traffic;\n')
                text('    document.getElementById(\"stations\").innerHTML = obj.stations;\n')
                text('  }\n')
                text('}, '+str(refresh*1000)+');\n')
            with tag('div', id='wrapper'):
                with tag('table', id='stations', klass='styled-table'):
                    pass
                with tag('br'):
                    pass
                with tag('table', id='traffic', klass='styled-table'):
                    pass
                with tag('br'):
                    pass
                with tag('a', href='https://github.com/jfrancis42/js8net', target='_blank'):
                    text('js8net')
                text(' by ')
                with tag('a', href='https://www.qrz.com/db/N0GQ', target='_blank'):
                    text('N0GQ')
    return(doc.getvalue())

def missing_page ():
    doc, tag, text=Doc().tagtext()
    global refresh
    with tag('html', lang='en'):
        with tag('body'):
            with tag('div', id='wrapper'):
                text('This page does not exist...')
    return(doc.getvalue())

def stations_table ():
    global stations
    global uuids
    global max_age
    doc, tag, text=Doc().tagtext()
    with tag('thead'):
        with tag('tr'):
            with tag('th'):
                text('TRX')
            with tag('th'):
                text('Call')
            with tag('th'):
                text('Grid')
            with tag('th'):
                text('Host')
            with tag('th'):
                text('Port')
            with tag('th'):
                text('Speed')
            with tag('th'):
                text('Dial')
            with tag('th'):
                text('Carrier')
#            with tag('th'):
#                text('Grid')
#            with tag('th'):
#                text('Heartbeat')
    for u in list(stations.keys()):
        if(stations[u]['time']>=time.time()-max_age):
            with tag('tr'):
                with tag('td', style='text-align:center;padding:6px'):
                    text(str(uuids[u]))
                with tag('td', style='text-align:center;padding:6px'):
                    text(stations[u]['call'])
                with tag('td', style='text-align:center;padding:6px'):
                    text(stations[u]['grid'])
                with tag('td', style='text-align:center;padding:6px'):
                    text(stations[u]['host'])
                with tag('td', style='text-align:center;padding:6px'):
                    text(str(stations[u]['port']))
                with tag('td', style='text-align:center;padding:6px'):
                    text(speed_name(int(stations[u]['speed'])))
                with tag('td', style='text-align:center;padding:6px'):
                    text(str(stations[u]['dial']/1000.0)+' khz')
                with tag('td', style='text-align:center;padding:6px'):
                    text(str(stations[u]['carrier'])+' hz')
#                with tag('td', style='text-align:center;padding:6px'):
#                    with tag('form', action='/', method='post'):
#                        with tag('input', type='hidden', value='true', name='send-grid'):
#                            pass
#                        with tag('input', type='hidden', value=u, name='uuid'):
#                            pass
#                        with tag('input', type='submit', value='Send'):
#                            pass
#                with tag('td', style='text-align:center;padding:6px'):
#                    with tag('form', action='/', method='post'):
#                        with tag('input', type='hidden', value='true', name='send-hb'):
#                            pass
#                        with tag('input', type='hidden', value=u, name='uuid'):
#                            pass
#                        with tag('input', type='submit', value='Send'):
#                            pass
    return(doc.getvalue())

def traffic_table():
    global traffic
    global traffic_lock
    global calls
    global mycall
    global uuids
    global max_age
    doc, tag, text=Doc().tagtext()
    with tag('thead'):
        with tag('tr'):
            with tag('th'):
                text('TRX')
            with tag('th'):
                text('Call')
            with tag('th'):
                text('Destination')
            with tag('th'):
                text('Grid')
            with tag('th'):
                text('Age')
            with tag('th'):
                text('SNR')
            with tag('th'):
                text('Speed')
            with tag('th'):
                text('Freq')
            if(len(calls)>0):
                with tag('th'):
                    text('Station(s)')
            with tag('th'):
                text('Received Text')
    # https://pskreporter.info/pskmap.html?preset&callsign=n0gq&timerange=1800&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1&mapCenter=39.09371454584385,-97.249548593876,5.3519901583255205
    with traffic_lock:
        for tfc in sorted(traffic,reverse=True,key=lambda n: n['time']):
            if(tfc['type']=='RX.DIRECTED' and tfc['time']>=time.time()-max_age):
                with tag('tr'):
                    with tag('td', style='text-align:center;padding:6px'):
                        text(str(uuids[tfc['uuid']]))
                    with tag('td', style='text-align:center;padding:6px'):
                        if('FROM' in tfc['params']):
                            with tag('a', href='https://pskreporter.info/pskmap.html?preset&callsign='+
                                     (tfc['params']['FROM'].split('/'))[0]+
                                     '&timerange=1800&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1&mapCenter=39.09371454584385,-97.249548593876,5.3519901583255205',
                                     target='_blank'):
                                text(tfc['params']['FROM'])
                        else:
                            text('')
                        if('TO' in tfc['params']):
                            if(tfc['params']['TO']==mycall):
                                with tag('td', style='text-align:center;background-color:#2ECC71'):
                                    with tag('a', href='https://pskreporter.info/pskmap.html?preset&callsign='+
                                             (tfc['params']['TO'].split('/'))[0]+
                                             '&timerange=1800&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1&mapCenter=39.09371454584385,-97.249548593876,5.3519901583255205',
                                             target='_blank'):
                                        text(tfc['params']['TO'])
                            elif(tfc['params']['TO'][0]=='@'):
                                with tag('td', style='text-align:center;background-color:#3498DB'):
                                    text(tfc['params']['TO'])
                            else:
                                with tag('td', style='text-align:center'):
                                    with tag('a', href='https://pskreporter.info/pskmap.html?preset&callsign='+
                                             (tfc['params']['TO'].split('/'))[0]+
                                             '&timerange=1800&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1&mapCenter=39.09371454584385,-97.249548593876,5.3519901583255205',
                                             target='_blank'):
                                        text(tfc['params']['TO'])
                        else:
                            with tag('td'):
                                text('')
                        if('GRID' in tfc['params']):
                            with tag('td', style='text-align:center'):
                                text(tfc['params']['GRID'])
                        else:
                            text('')
                        with tag('td', style='text-align:center'):
                            if('time' in tfc):
                                text(str(int(time.time()-tfc['time']))+' sec')
                            else:
                                text('')
                        if('SNR' in  tfc['params']):
                            snr=tfc['params']['SNR']
                            if(snr>=-10):
                                s='text-align:center;background-color:#7CD342'
                            elif(snr<-10 and snr>=-17):
                                s='text-align:center;background-color:#FDD835'
                            elif(snr<-17):
                                s='text-align:center;background-color:#F4511E'
                        else:
                            s='text-align:center'
                        with tag('td', style=s):
                            if('SNR' in tfc['params']):
                                text(str(snr)+' db')
                            else:
                                text('')
                        with tag('td', style='padding:6px;text-align:center'):
                            if('SPEED' in tfc['params']):
                                text(speed_name(tfc['params']['SPEED']))
                            else:
                                text('')
                        with tag('td', style='padding:6px'):
                            if('FREQ' in tfc['params']):
                                text((str(tfc['params']['FREQ']/1000.0))+' khz')
                            else:
                                text('')
                        if(len(calls)>0):
                            with tag('td', style='padding:6px'):
                                if('FROM' in tfc['params']):
                                    fmcall=tfc['params']['FROM'].split('/')[0]
                                    tocall=tfc['params']['TO'].split('/')[0]
                                    with tag('table'):
                                        with tag('tr'):
                                            with tag('td'):
                                                with tag('a', href='http://www.qrz.com/db/'+fmcall, target='_blank'):
                                                    text(fmcall)
                                            with tag('td'):
                                                if(fmcall in calls):
                                                    text(', '.join(calls[fmcall]))
                                        with tag('tr'):
                                            with tag('td'):
                                                if(len(tocall)>0):
                                                    if(tocall[0]=='@'):
                                                        text(tocall)
                                                    else:
                                                        with tag('a', href='http://www.qrz.com/db/'+tocall, target='_blank'):
                                                            text(tocall)
                                                else:
                                                    text('')
                                            with tag('td'):
                                                if(tocall in calls):
                                                    text(', '.join(calls[tocall]))
                                else:
                                    text('')
                        with tag('td', style='padding:6px'):
                            if('TEXT' in tfc['params']):
                                text(tfc['params']['TEXT'])
                            else:
                                text('')
    return(doc.getvalue())

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global stations
        global traffic
        global traffic_lock
        global aggregator
        global uuids
        global uindex
        doc, tag, text=Doc().tagtext()
        if(self.path=='/'):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str.encode(main_page()))
        elif(self.path=='/jsstatus'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            r=requests.get('http://'+aggregator+'/fetch')
            stations=r.json()['stations']
            with traffic_lock:
                traffic=r.json()['traffic']
            for u in list(stations.keys()):
                if(u in uuids.keys()):
                    pass
                else:
                    print('Assigning uindex '+str(uindex)+' to uuid '+u)
                    uuids[u]=uindex
                    uindex=uindex+1
            j={'stations': stations_table(),
               'traffic': traffic_table(),
               'complete': '0'}
            self.wfile.write(str.encode(json.dumps(j)))
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str.encode(missing_page()))

def calls_thread(name):
    global calls
    calls={}
    time.sleep(5)
    if(exists('EN.dat')):
        print('Loading callsign records...')
        with open('EN.dat', 'r', encoding='utf8') as ham_file:
            ham_reader=csv.reader(ham_file, delimiter='|')
            for row in ham_reader:
                call=row[4]
                name=row[7]
                city=row[16]
                state=row[17]
                calls[call]=[name,city,state]
        print('Done.')

def graph_thread(name):
    global traffic
    global traffic_lock
    global max_age
    while(True):
        time.sleep(30)
        with traffic_lock:
            f=open('traffic.dot','w')
            f.write('digraph {\n')
            # "foo" -> "bar";
            for tfc in traffic:
                if(tfc['type']=='RX.DIRECTED' and tfc['time']>=time.time()-max_age):
                    if('FROM' in tfc['params'] and 'TO' in tfc['params']):
                        if(tfc['params']['TO']!='@HB' and tfc['params']['TO']!='@ALLCALL'):
                            if(tfc['params']['TO'][0]=='@'):
                                f.write('  "'+(tfc['params']['FROM'].split('/'))[0]+
                                        '" -> "\\'+(tfc['params']['TO'].split('/'))[0]+'";\n')
                            else:
                                f.write('  "'+(tfc['params']['FROM'].split('/'))[0]+
                                        '" -> "'+(tfc['params']['TO'].split('/'))[0]+'";\n')
            f.write('}\n')
            f.close()        
        os.system('dot -Tjpg traffic.dot -o traffic.jpg')

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# Main program.
if(__name__ == '__main__'):
    parser=argparse.ArgumentParser(description='Monitor JS8Call Traffic.')
    parser.add_argument('--call',default=False,help='My Call')
    parser.add_argument('--aggregator',default=False,help='IP/DNS and port of JS8Call server (default localhost:8001)')
    parser.add_argument('--web_port',default=False,help='TCP port of for the web server (default 8000)')
    parser.add_argument('--refresh',default=False,help='Web page refresh time in seconds (default 3.0)')
    parser.add_argument('--max_age',default=False,help='Maximum traffic age (default 1800 seconds)')
    args=parser.parse_args()

    traffic_lock=threading.Lock()
    traffic=[]
    stations=[]
    uuids={}
    uindex=0
    
    if(args.call):
        mycall=args.call.upper()
    else:
        mycall='XYZZY123'

    if(args.aggregator):
        aggregator=args.aggregator
    else:
        aggregator='localhost:8001'

    if(args.web_port):
        webport=int(args.web_port)
    else:
        webport=8000

    if(args.refresh):
        refresh=int(args.refresh)
    else:
        refresh=3.0

    if(args.max_age):
        max_age=int(args.max_age)
    else:
        max_age=1800
    print('Max age: '+str(max_age))

    thread0=Thread(target=calls_thread,args=('Calls Thread',),daemon=True)
    thread0.start()
    thread1=Thread(target=graph_thread,args=('Graph Thread',),daemon=True)
    thread1.start()

    httpd=HTTPServer(('0.0.0.0', webport), SimpleHTTPRequestHandler)
    httpd.serve_forever()
#    pdb.set_trace()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# if(type(stations[u]['carrier']).__name__ =='str'):
# https://stackoverflow.com/questions/14784405/how-to-set-the-output-size-in-graphviz-for-the-dot-format

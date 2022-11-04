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
import datetime
from os.path import exists
from js8net import *
import pyproj
#import pdb
import csv
import requests
import maidenhead as mh
#from urllib.parse import urlparse, parse_qs
import urllib
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

global tx_allowed
tx_allowed=False

global css
global color_mycall
global color_at
global color_snr_supergreen
global color_snr_green
global color_snr_yellow
global color_snr_red
global color_heartbeat
global color_query
global color_table_header_background
global color_table_header_text
global color_link
global color_border_bottom_odd
global color_border_bottom_even
global color_border_bottom_last

color_mycall='#2ECC71'
color_at='#5DADE2'
color_snr_supergreen='#66FF00'
color_snr_green='#7CD342'
color_snr_yellow='#FDD835'
color_snr_red='#F4511E'
color_heartbeat='#FADBD8'
color_query='#D6EAF8'
color_table_header_background='#08389F'
color_table_header_text='#FFFFFF'
color_link='#000000'
color_border_bottom_odd='#DDDDDD'
color_border_bottom_even='#F3F3F3'
color_border_bottom_last='#009879'

css="""
a {
  color: '+color_link+';
  text-decoration: none;
  text-transform: uppercase;
}
.styled-table {
    border-collapse: collapse;
    margin: 25px 0;
    font-size: 0.9em;
    font-family: sans-serif;
    min-width: 400px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
}
.styled-table thead tr {
    background-color: '+color_table_header_background+';
    color: '+color_table_header_text+';
    text-align: left;
}
.styled-table th,
.styled-table td {
    padding: 12px 15px;
}
.styled-table tbody tr {
    border-bottom: 1px solid '+color_border_bottom_odd+';
}
.styled-table tbody tr:nth-of-type(even) {
    background-color: '+color_border_bottom_even+';
}
.styled-table tbody tr:last-of-type {
    border-bottom: 2px solid '+color_border_bottom_last+';
}
"""

def aprs_page (r):
    global color_table_header_background
    global color_table_header_text
    global color_border_bottom_odd
    global color_border_bottom_even
    global color_border_bottom_last
    global color_link
    global stations
    global css
    doc, tag, text=Doc().tagtext()
    with tag('html', lang='en'):
        with tag('head'):
            with tag('style'):
                text(css)
        with tag('body'):
            with tag('div', id='wrapper'):
                with tag('h1'):
                    text('Send an APRS message from '+stations[r['uuid']]['call']+'\'s')
                    if(stations[r['uuid']]['radio'] and stations[r['uuid']]['radio']!=''):
                        text(' '+stations[r['uuid']]['radio'])
                    text(' radio on '+str(stations[r['uuid']]['dial']/1000.0)+' khz.')
                with tag('br'):
                    pass
                with tag('form', action='/', method='post'):
                    with tag('input', type='hidden', value='send-aprs', name='cmd'):
                        pass
                    with tag('input', type='hidden', value=r['uuid'], name='uuid'):
                        pass
                    with tag('table', klass='styled-table'):
                        with tag('tr'):
                            with tag('td'):
                                text('Call')
                            with tag('td'):
                                with tag('input', type='text', name='aprs-call'):
                                    pass
                        with tag('tr'):
                            with tag('td'):
                                text('Content')
                            with tag('td'):
                                with tag('input', type='text', name='content', size='200'):
                                    pass
                        with tag('tr'):
                            with tag('td'):
                                pass
                            with tag('td'):
                                with tag('input', type='submit', value='Submit'):
                                    pass
                with tag('br'):
                    text('Note that @APRSIS truncates all messages to 67 characters maximum length.')
    return(doc.getvalue())

def text_page (r):
    global color_table_header_background
    global color_table_header_text
    global color_border_bottom_odd
    global color_border_bottom_even
    global color_border_bottom_last
    global color_link
    global stations
    global css
    doc, tag, text=Doc().tagtext()
    with tag('html', lang='en'):
        with tag('head'):
            with tag('style'):
                text(css)
        with tag('body'):
            with tag('div', id='wrapper'):
                with tag('h1'):
                    text('Send a text message from '+stations[r['uuid']]['call']+'\'s')
                    if(stations[r['uuid']]['radio'] and stations[r['uuid']]['radio']!=''):
                        text(' '+stations[r['uuid']]['radio'])
                    text(' radio on '+str(stations[r['uuid']]['dial']/1000.0)+' khz.')
                with tag('br'):
                    pass
                with tag('form', action='/', method='post'):
                    with tag('input', type='hidden', value='send-text', name='cmd'):
                        pass
                    with tag('input', type='hidden', value=r['uuid'], name='uuid'):
                        pass
                    with tag('table', klass='styled-table'):
                        with tag('tr'):
                            with tag('td'):
                                text('Phone')
                            with tag('td'):
                                with tag('input', type='text', name='phone'):
                                    pass
                        with tag('tr'):
                            with tag('td'):
                                text('Content')
                            with tag('td'):
                                with tag('input', type='text', name='content', size='200'):
                                    pass
                        with tag('tr'):
                            with tag('td'):
                                pass
                            with tag('td'):
                                with tag('input', type='submit', value='Submit'):
                                    pass
                with tag('br'):
                    text('Note that @APRSIS truncates all messages to 67 characters maximum length.')
    return(doc.getvalue())

def email_page (r):
    global color_table_header_background
    global color_table_header_text
    global color_border_bottom_odd
    global color_border_bottom_even
    global color_border_bottom_last
    global color_link
    global css
    doc, tag, text=Doc().tagtext()
    with tag('html', lang='en'):
        with tag('head'):
            with tag('style'):
                text(css)
        with tag('body'):
            with tag('div', id='wrapper'):
                with tag('h1'):
                    text('Send an email message from '+stations[r['uuid']]['call']+'\'s')
                    if(stations[r['uuid']]['radio'] and stations[r['uuid']]['radio']!=''):
                        text(' '+stations[r['uuid']]['radio'])
                    text(' radio on '+str(stations[r['uuid']]['dial']/1000.0)+' khz.')
                with tag('br'):
                    pass
                with tag('form', action='/', method='post'):
                    with tag('input', type='hidden', value='send-email', name='cmd'):
                        pass
                    with tag('input', type='hidden', value=r['uuid'], name='uuid'):
                        pass
                    with tag('table', klass='styled-table'):
                        with tag('tr'):
                            with tag('td'):
                                text('Address')
                            with tag('td'):
                                with tag('input', type='text', name='addr'):
                                    pass
                        with tag('tr'):
                            with tag('td'):
                                text('Content')
                            with tag('td'):
                                with tag('input', type='text', name='content', size='200'):
                                    pass
                        with tag('tr'):
                            with tag('td'):
                                pass
                            with tag('td'):
                                with tag('input', type='submit', value='Submit'):
                                    pass
                with tag('br'):
                    text('Note that @APRSIS truncates all messages to 67 characters maximum length.')
    return(doc.getvalue())

def main_page ():
    global css
    global refresh
    global color_table_header_background
    global color_table_header_text
    global color_border_bottom_odd
    global color_border_bottom_even
    global color_border_bottom_last
    global color_link
    doc, tag, text=Doc().tagtext()
    with tag('html', lang='en'):
        with tag('head'):
            with tag('style'):
                text(css)
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
                text('function myFunction() {')
                text('  var x = document.getElementById("stations");')
                text('  if (x.style.display === "none") {')
                text('    x.style.display = "block";')
                text('  } else {')
                text('    x.style.display = "none";')
                text('  }')
                text('}')
            with tag('div', id='wrapper'):
                with tag('h1'):
                    text('Stations')
                with tag('table', id='stations', klass='styled-table'):
                    pass
                with tag('button', onclick='myFunction()'):
                    text('Show/Hide Stations')
                with tag('br'):
                    pass
                with tag('h1'):
                    text('Traffic')
                with tag('table', id='traffic', klass='styled-table'):
                    pass
                with tag('br'):
                    pass
                with tag('a', href='https://github.com/jfrancis42/js8net', target='_blank'):
                    text('js8net')
                text(' by ')
                with tag('a', href='https://www.qrz.com/db/N0GQ', target='_blank'):
                    text('N0GQ')
                with tag('br'):
                    pass
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
    global tx_allowed
    doc, tag, text=Doc().tagtext()
    with tag('thead'):
        with tag('tr'):
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
            with tag('th'):
                text('Radio')
            if(tx_allowed):
                with tag('th'):
                    text('Heartbeat')
                with tag('th'):
                    text('Grid')
                with tag('th'):
                    text('Text')
                with tag('th'):
                    text('Email')
                with tag('th'):
                    text('APRS')
    for u in list(stations.keys()):
        if(stations[u]['time']>=time.time()-max_age):
            with tag('tr'):
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
                with tag('td', style='text-align:center;padding:6px'):
                    if('radio' in stations[u]):
                        text(stations[u]['radio'])
                    else:
                        text('unknown')
                if(tx_allowed and stations[u]['tx']):
                    with tag('td', style='text-align:center;padding:6px'):
                        with tag('form', action='/', method='post'):
                            with tag('input', type='hidden', value='send-hb', name='cmd'):
                                pass
                            with tag('input', type='hidden', value=u, name='uuid'):
                                pass
                            with tag('input', type='submit', value='Send'):
                                pass
                    with tag('td', style='text-align:center;padding:6px'):
                        with tag('form', action='/', method='post'):
                            with tag('input', type='hidden', value='send-grid', name='cmd'):
                                pass
                            with tag('input', type='hidden', value=u, name='uuid'):
                                pass
                            with tag('input', type='submit', value='Send'):
                                pass
                    with tag('td', style='text-align:center;padding:6px'):
                        with tag('form', action='/text', method='get'):
                            with tag('input', type='hidden', value='text', name='type'):
                                pass
                            with tag('input', type='hidden', value=u, name='uuid'):
                                pass
                            with tag('input', type='submit', value='Send'):
                                pass
                    with tag('td', style='text-align:center;padding:6px'):
                        with tag('form', action='/email', method='get'):
                            with tag('input', type='hidden', value='email', name='type'):
                                pass
                            with tag('input', type='hidden', value=u, name='uuid'):
                                pass
                            with tag('input', type='submit', value='Send'):
                                pass
                    with tag('td', style='text-align:center;padding:6px'):
                        with tag('form', action='/aprs', method='get'):
                            with tag('input', type='hidden', value='aprs', name='type'):
                                pass
                            with tag('input', type='hidden', value=u, name='uuid'):
                                pass
                            with tag('input', type='submit', value='Send'):
                                pass
    return(doc.getvalue())

def traffic_table():
    global traffic
    global traffic_lock
    global calls
    global mycall
    global uuids
    global max_age
    global color_mycall
    global color_at
    global color_snr_supergreen
    global color_snr_green
    global color_snr_yellow
    global color_snr_red
    global color_heartbeat
    global color_query
    lat=False
    lon=False
    geodesic=pyproj.Geod(ellps='WGS84')
    doc, tag, text=Doc().tagtext()
    with tag('thead'):
        with tag('tr'):
            with tag('th'):
                text('Station')
            with tag('th'):
                text('Call')
            with tag('th'):
                text('Destination')
            with tag('th'):
                text('Grid')
            with tag('th'):
                text('Dist')
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
                    text('Stations - (Click for qrz.com)')
            with tag('th'):
                text('Received Text')
    with traffic_lock:
        for tfc in sorted(traffic,reverse=True,key=lambda n: n['time']):
            if(tfc['type']=='RX.DIRECTED' and tfc['time']>=time.time()-max_age):
                with tag('tr'):
                    with tag('td', style='text-align:center;padding:6px'):
                        if(tfc['uuid'] in uuids):
#                            text(str(uuids[tfc['uuid']]))
                            text(stations[tfc['uuid']]['call'])
                            with tag('br'):
                                pass
                            text(stations[tfc['uuid']]['radio'])
                        else:
                            text('unknown')
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
                                with tag('td', style='text-align:center;background-color:'+color_mycall):
                                    with tag('a', href='https://pskreporter.info/pskmap.html?preset&callsign='+
                                             (tfc['params']['TO'].split('/'))[0]+
                                             '&timerange=1800&hideunrec=1&blankifnone=1&hidepink=1&showsnr=1&showlines=1&mapCenter=39.09371454584385,-97.249548593876,5.3519901583255205',
                                             target='_blank'):
                                        text(tfc['params']['TO'])
                            elif(tfc['params']['TO'][0]=='@'):
                                with tag('td', style='text-align:center;background-color:'+color_at):
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
                            if('lat' in stations[tfc['uuid']] and
                               'lon' in stations[tfc['uuid']] and
                               tfc['params']['GRID']!=''):
                                if(len(tfc['params']['GRID'])>8):
                                    (lat,lon)=mh.to_location(tfc['params']['GRID'][0:8])
                                else:
                                    (lat,lon)=mh.to_location(tfc['params']['GRID'])
                                (fwd_azimuth,back_azimuth,distance)=geodesic.inv(stations[tfc['uuid']]['lon'],
                                                                                 stations[tfc['uuid']]['lat'],
                                                                                 lon,lat)
                                text(str(round(distance/1000*0.6214))+' mi')
                                with tag('br'):
                                    pass
                                if(fwd_azimuth<0):
                                    text(str(round(fwd_azimuth+360))+' deg')
                                else:
                                    text(str(round(fwd_azimuth))+' deg')
                            else:
                                text('')
                        with tag('td', style='text-align:center'):
                            if('time' in tfc):
                                text(str(datetime.timedelta(seconds=int(time.time()-tfc['time']))))
                            else:
                                text('')
                        if('SNR' in  tfc['params']):
                            snr=tfc['params']['SNR']
                            if(snr>0):
                                s='text-align:center;background-color:'+color_snr_supergreen
                            if(snr>=-10 and snr<=0):
                                s='text-align:center;background-color:'+color_snr_green
                            elif(snr<-10 and snr>=-17):
                                s='text-align:center;background-color:'+color_snr_yellow
                            elif(snr<-17):
                                s='text-align:center;background-color:'+color_snr_red
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
                                                else:
                                                    text('unknown')
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
                                                if(tocall[0]=='@'):
                                                    pass
                                                else:
                                                    if(tocall in calls):
                                                        text(', '.join(calls[tocall]))
                                                    else:
                                                        text('unknown')
                                else:
                                    text('')
                        c='#FFFFFF'
                        if('TO' in tfc['params']):
                            if(len(tfc['params']['TO'])==3):
                                if(tfc['params']['TO']=='@HB'):
                                    c=color_heartbeat
                            if('TEXT' in tfc['params']):
                                tmp=tfc['params']['TEXT'].split()
                                if(len(tmp)>=3):
                                    if(tmp[2]=='HEARTBEAT'):
                                        c=color_heartbeat
                                    if(tmp[2]=='SNR' or tmp[2]=='SNR?' or
                                       tmp[2]=='INFO' or tmp[2]=='INFO?' or
                                       tmp[2]=='GRID' or tmp[2]=='GRID?' or
                                       tmp[2]=='ACK' or tmp[2]=='QUERY'):
                                        c=color_query
                        if('TEXT' in tfc['params']):
                            if('@ALLCALL CQ' in tfc['params']['TEXT']):
                                c='#FCF3CF' # cq
                        with tag('td', style='padding:6px;background-color:'+c):
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
#        print('===========================================')
#        print(self.path)
#        print('===========================================')
        if('/text?' in self.path):
            self.send_response(200)
            self.end_headers()
            r=dict(urllib.parse.parse_qsl(self.path))
            print('===========================================')
            print(r)
            print('===========================================')
            self.wfile.write(str.encode(text_page(r)))
        elif('/email?' in self.path):
            self.send_response(200)
            self.end_headers()
            r=dict(urllib.parse.parse_qsl(self.path))
            print('===========================================')
            print(r)
            print('===========================================')
            self.wfile.write(str.encode(email_page(r)))
        elif('/aprs?' in self.path):
            self.send_response(200)
            self.end_headers()
            r=dict(urllib.parse.parse_qsl(self.path))
            print('===========================================')
            print(r)
            print('===========================================')
            self.wfile.write(str.encode(aprs_page(r)))
        elif(self.path=='/'):
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

    def do_POST(self):
        content_length=int(self.headers['Content-Length'])
        payload=self.rfile.read(content_length).decode('utf8')
        print('--------------------')
        print(payload)
        print('--------------------')
        p=dict(urllib.parse.parse_qsl(payload))
        print('=====================')
        print(p)
        print('=====================')
        if(self.path=='/'):
            self.send_response(200)
            self.end_headers()
            res=requests.post('http://'+aggregator+'/cmd',json=p)
            print(res)
            self.wfile.write(str.encode(main_page()))

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
    parser.add_argument('--transmit',default=False,help='Provide transmit options in UI (default is rx only)',
                        action='store_true')
    parser.add_argument('--aggregator',default=False,help='IP/DNS and port of JS8Call aggregator (default localhost:8001)')
    parser.add_argument('--web_port',default=False,help='TCP port of for the web server (default 8000)')
    parser.add_argument('--refresh',default=False,help='Web page refresh time in seconds (default 3.0)')
    parser.add_argument('--max_age',default=False,help='Maximum traffic age (default 1800 seconds)')
    parser.add_argument('--localhost',default=False,help='Bind to localhost only (default 0.0.0.0)',
                        action='store_true')
    args=parser.parse_args()

    traffic_lock=threading.Lock()
    traffic=[]
    stations=[]
    uuids={}
    uindex=0
    
    tx_allowed=args.transmit

    if(args.call):
        mycall=args.call.upper()
    else:
        mycall=''

    if(args.aggregator):
        aggregator=args.aggregator
    else:
        aggregator='localhost:8001'

    if(args.localhost):
        localhost=True
    else:
        localhost=False

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

    if(localhost):
        httpd=HTTPServer(('127.0.0.1', webport), SimpleHTTPRequestHandler)
    else:
        httpd=HTTPServer(('0.0.0.0', webport), SimpleHTTPRequestHandler)
    httpd.serve_forever()
#    pdb.set_trace()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

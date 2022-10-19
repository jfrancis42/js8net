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
import pdb
import csv

from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from yattag import Doc
import json

global js8host
global js8port
global mycall
global mygrid
global myinfo
global myfreq
global myspeed
global max_age
global traffic

global calls
global refresh

global traffic_lock
traffic_lock=threading.Lock()

def get_their_grid(theircall):
    if(mycall in spots):
        if(theircall in spots[mycall]):
            tmp=list(filter(lambda n: n['grid']!=False, spots[mycall][theircall]))
            if(len(tmp)>0):
                return(tmp[0]['grid'])
    return(False)

def email_form ():
    doc, tag, text=Doc().tagtext()
    with tag('html', lang='en'):
        with tag('body'):
            with tag('form', action='/', method='post'):
                with tag('input', type='hidden', value='fart'):
                    pass
                with tag('table'):
                    with tag('tr'):
                        with tag('td'):
                            text('Destination:')
                        with tag('td'):
                            with tag('input', name='destination', size=50):
                                pass
                    with tag('tr'):
                        with tag('td'):
                            text('Message:')
                        with tag('td'):
                            with tag('input', name='message', size=100):
                                pass
                with tag('input', type='submit', value='Query'):
                    pass

def text_form ():
    pass

def traffic_table ():
    global max_age
    global traffic
    global traffic_lock
    global mycall
    global calls
    doc, tag, text=Doc().tagtext()
    with tag('tr'):
        with tag('th', style='background-color:#C0C0C0'):
            text('Call')
        with tag('th', style='background-color:#C0C0C0'):
            text('Destination')
        with tag('th', style='background-color:#C0C0C0'):
            text('Grid')
        with tag('th', style='background-color:#C0C0C0'):
            text('Age')
        with tag('th', style='background-color:#C0C0C0'):
            text('SNR')
        with tag('th', style='background-color:#C0C0C0'):
            text('Speed')
        with tag('th', style='background-color:#C0C0C0'):
            text('Freq')
        with tag('th', style='background-color:#C0C0C0'):
            text('Calls')
        with tag('th', style='background-color:#C0C0C0'):
            text('Text')
    with rx_lock:
        with traffic_lock:
            for tfc in sorted(traffic,reverse=True,key=lambda n: n['time']):
                if(tfc['type']=='RX.DIRECTED' and tfc['time']>=time.time()-max_age):
                    with tag('tr'):
                        with tag('td', style='text-align:center'):
                            if('FROM' in tfc['params']):
                                text(tfc['params']['FROM'])
                            else:
                               text('')
                            if('TO' in tfc['params']):
                                if(tfc['params']['TO']==mycall):
                                    with tag('td', style='text-align:center;background-color:#2ECC71'):
                                        text(tfc['params']['TO'])
                                elif(tfc['params']['TO'][0]=='@'):
                                    with tag('td', style='text-align:center;background-color:#3498DB'):
                                        text(tfc['params']['TO'])
                                else:
                                    with tag('td', style='text-align:center'):
                                        text(tfc['params']['TO'])
                            else:
                                with tag('td'):
                                    text('')
                            if('GRID' in tfc['params'] and tfc['params']['GRID']!=''):
                                with tag('td', style='text-align:center'):
                                    text(tfc['params']['GRID'])
                            elif(get_their_grid(tfc['params']['FROM'])):
                                with tag('td', style='text-align:center'):
                                    text(get_their_grid(tfc['params']['FROM']))
                            else:
                                with tag('td', style='text-align:center;background-color:#C0C0C0'):
                                    with tag('form', action='/', method='post'):
                                        with tag('input', type='hidden', value=tfc['params']['FROM'], name='get-grid'):
                                            pass
                                        with tag('input', type='submit', value='Query'):
                                            pass
                        with tag('td', style='text-align:center'):
                            if('time' in tfc):
                                text(str(int(time.time()-tfc['time']))+" sec")
                            else:
                               text('')
                        with tag('td', style='text-align:center'):
                            if('SNR' in tfc['params']):
                                text(str(tfc['params']['SNR'])+' db')
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
                        with tag('td', style='padding:6px'):
                            fmcall=tfc['params']['FROM'].split('/')[0]
                            tocall=tfc['params']['TO'].split('/')[0]
                            with tag('table'):
                                with tag('tr'):
                                    with tag('td'):
                                        text(fmcall)
                                    with tag('td'):
                                        if(fmcall in calls):
                                            text(', '.join(calls[fmcall]))
                                with tag('tr'):
                                    with tag('td'):
                                        text(tocall)
                                    with tag('td'):
                                        if(tocall in calls):
                                            text(', '.join(calls[tocall]))
                        with tag('td', style='padding:6px'):
                            text(tfc['params']['TEXT'])
    return(doc.getvalue())

def main_page ():
    doc, tag, text=Doc().tagtext()
    global refresh
    with tag('html', lang='en'):
        with tag('body'):
            with tag('script', type='text/javascript'):
                text('\nvar intervalId = setInterval(function() {\n')
                text('  getText(\"/jsstatus\");\n')
                text('  async function getText(file) {\n')
                text('    let myObject = await fetch(file);\n')
                text('    let myText = await myObject.text();\n')
                text('    var obj = JSON.parse(myText);\n')
                text('    document.getElementById(\"time\").innerHTML = obj.time;\n')
                text('    document.getElementById(\"call\").innerHTML = obj.call;\n')
                text('    document.getElementById(\"grid\").innerHTML = obj.grid;\n')
                text('    document.getElementById(\"host\").innerHTML = obj.host;\n')
                text('    document.getElementById(\"port\").innerHTML = obj.port;\n')
                text('    document.getElementById(\"speed\").innerHTML = obj.speed;\n')
                text('    document.getElementById(\"carrier\").innerHTML = obj.carrier;\n')
                text('    document.getElementById(\"dial\").innerHTML = obj.dial;\n')
                text('    document.getElementById(\"traffic\").innerHTML = obj.traffic;\n')
                text('    if(obj.complete==1) {\n')
                text('      location.href = \"/fixme\";\n')
                text('      clearInterval(intervalId);\n')
                text('    }\n')
                text('  }\n')
                text('}, '+str(refresh*1000)+');\n')
            with tag('div', id='wrapper'):
                with tag('table'):
                    with tag('tr'):
                        with tag('td'):
                            text('Time:')
                        with tag('td'):
                            with tag('p', id='time'):
                                text('unknown')
                    with tag('tr'):
                        with tag('td'):
                            text('Call:')
                        with tag('td'):
                            with tag('p', id='call'):
                                text('unknown')
                    with tag('tr'):
                        with tag('td'):
                            text('Grid:')
                        with tag('td'):
                            with tag('p', id='grid'):
                                text('unknown')
                    with tag('tr'):
                        with tag('td'):
                            text('Host:')
                        with tag('td'):
                            with tag('p', id='host'):
                                text('unknown')
                    with tag('tr'):
                        with tag('td'):
                            text('Port:')
                        with tag('td'):
                            with tag('p', id='port'):
                                text('unknown')
                    with tag('tr'):
                        with tag('td'):
                            text('Speed:')
                        with tag('td'):
                            with tag('p', id='speed'):
                                text('unknown')
                    with tag('tr'):
                        with tag('td'):
                            text('Dial Freq:')
                        with tag('td'):
                            with tag('p', id='dial'):
                                text('unknown')
                    with tag('tr'):
                        with tag('td'):
                            text('Carrier Freq:')
                        with tag('td'):
                            with tag('p', id='carrier'):
                                text('unknown')
                with tag('br'):
                    pass
                with tag('table'):
                    with tag('tr'):
                        with tag('td'):
                            with tag('form', action='/', method='post'):
                                with tag('input', type='hidden', value='true', name='send-grid'):
                                    pass
                                with tag('input', type='submit', value='Send Grid'):
                                    pass
                        with tag('td'):
                            with tag('form', action='/', method='post'):
                                with tag('input', type='hidden', value='true', name='send-hb'):
                                    pass
                                with tag('input', type='submit', value='Send Heartbeat'):
                                    pass
                        with tag('td'):
                            with tag('form', action='/', method='post'):
                                with tag('input', type='hidden', value='true', name='send-text'):
                                    pass
                                with tag('input', type='submit', value='Send Text Message'):
                                    pass
                        with tag('td'):
                            with tag('form', action='/', method='post'):
                                with tag('input', type='hidden', value='true', name='send-email'):
                                    pass
                                with tag('input', type='submit', value='Send Email'):
                                    pass
                with tag('br'):
                    pass
                with tag('table', id='traffic', border=2):
                    pass
    return(doc.getvalue())

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        doc, tag, text=Doc().tagtext()
        global js8host
        global js8port
        global mycall
        global mygrid
        global myinfo
        global myfreq
        global myspeed
        if self.path=='/jsstatus':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            j={'time': time.asctime(),
               'call': mycall,
               'grid': mygrid,
               'host': js8host,
               'port': str(js8port),
               'speed': speed_name(int(myspeed)),
               'dial': str(myfreq['dial']/1000.0)+' khz',
               'carrier': str(myfreq['offset'])+' hz',
               'traffic': traffic_table(),
               'complete': '0'}
            self.wfile.write(str.encode(json.dumps(j)))
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str.encode(main_page()))

    def do_POST(self):
        global js8host
        global js8port
        global mycall
        global mygrid
        global myinfo
        global myfreq
        global myspeed
        content_length = int(self.headers['Content-Length'])
        parsed = parse_qs(self.rfile.read(content_length))
        print(parsed)
        if(b'send-grid' in parsed):
            send_aprs_grid(get_grid())
        if(b'send-hb' in parsed):
            send_heartbeat()
        if(b'get-grid' in parsed):
            call=parsed[b'get-grid'][0].decode()
            query_grid(call)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        if(b'send-email' in parsed):
            response.write(str.encode(email_form()))
        elif(b'send-text' in parsed):
            pass
        else:
            response.write(str.encode(main_page()))
        self.wfile.write(response.getvalue())

def update_thread(name):
    global js8host
    global js8port
    global mycall
    global mygrid
    global myinfo
    global myfreq
    global myspeed
    print(name+' started...')
    while(True):
        print("Fetching updated radio data...")
        mycall=get_callsign()
        mygrid=get_grid()
        myinfo=get_info()
        myfreq=get_freq()
        myspeed=get_speed()
        time.sleep(5.0)

def traffic_thread(name):
    global traffic
    global traffic_lock
    global max_age
    print(name+' started...')
    while(True):
        time.sleep(0.1)
        if(not(rx_queue.empty())):
            with rx_lock:
                rx=rx_queue.get()
            print('New traffic received...')
            if(rx['type']=='RX.DIRECTED' or rx['type']=='RX.ACTIVITY'):
                with traffic_lock:
                    traffic.append(rx)
                    traffic=list(filter(lambda n: n['time'] > time.time()-(max_age*2),traffic))
                    print(str(len(traffic)))
                    f=open("/tmp/traffic.json","w")
                    f.write(json.dumps(traffic))
                    f.write("\n")
                    f.close()
                with spots_lock:
                    f=open("/tmp/spots.json","w")
                    f.write(json.dumps(spots))
                    f.write("\n")
                    f.close()

def calls_thread(name):
    global calls
    calls={}
    if(exists('EN.dat')):
        print("Loading callsign records...")
        with open("EN.dat", "r", encoding="utf8") as ham_file:
            ham_reader = csv.reader(ham_file, delimiter="|")
        
            for row in ham_reader:
                call=row[4]
                name=row[7]
                addr=row[16]
                city=row[17]
                state=row[18]
                calls[call]=[name,addr,city,state]
        print("Done.")

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# Main program.
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Send JS8Call Heartbeat.")
    parser.add_argument("--js8_host",default=False,help="IP/DNS of JS8Call server (default localhost, env: JS8HOST)")
    parser.add_argument("--js8_port",default=False,help="TCP port of JS8Call server (default 2442, env: JS8PORT)")
    parser.add_argument("--web_port",default=False,help="TCP port of for the web server (default 8000, env: JS8WEBPORT)")
    parser.add_argument("--refresh",default=False,help="Web page refresh time in seconds (default 1.0, env: JS8REFRESH)")
    parser.add_argument("--env",default=False,action="store_true",help="Use environment variables (cli options override)")
    parser.add_argument("--verbose",default=False,action="store_true",help="Lots of status messages")
    args=parser.parse_args()

    js8host=False
    js8port=False
    webport=False

    mycall='unknown'
    mygrid='unknown'
    myinfo='unknown'
    myfreq={'dial': 0, 'freq': 0, 'offset': 0}
    myspeed='0'
    
    max_age=1800
    traffic=[]
    
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

    if(args.web_port):
        webport=int(args.js8_port)
    elif(os.environ.get("JS8WEBPORT") and args.env):
        webport=int(os.environ.get("JS8WEBPORT"))
    else:
        webport=8000

    if(args.refresh):
        refresh=int(args.refresh)
    elif(os.environ.get("JS8REFRESH") and args.env):
        refresh=int(os.environ.get("JS8REFRESH"))
    else:
        refresh=1.0

    if(args.verbose):
        print("Connecting to JS8Call...")
    start_net(js8host,js8port)
    if(args.verbose):
        print("Connected.")

    if(exists("/tmp/traffic.json")):
        with traffic_lock:
            f=open("/tmp/traffic.json")
            traffic=json.load(f)
            f.close()
    if(exists("/tmp/spots.json")):
        with spots_lock:
            f=open("/tmp/spots.json")
            spots=json.load(f)
            f.close()
    
    thread0=Thread(target=calls_thread,args=('Calls Thread',),daemon=True)
    thread0.start()
    thread1=Thread(target=update_thread,args=('Update Thread',),daemon=True)
    thread1.start()
    thread2=Thread(target=traffic_thread,args=('Traffic Thread',),daemon=True)
    thread2.start()
    
    httpd = HTTPServer(('0.0.0.0', webport), SimpleHTTPRequestHandler)
    httpd.serve_forever()
    pdb.set_trace()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

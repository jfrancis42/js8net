#!/usr/bin/env python3
# coding: utf-8

import sys
import socket
import json
import time
import threading
import traceback
from threading import Thread
from queue import Queue

# Defaults within JS8Call.
global eom
global error
global timeout
eom="♢"
error="…"
timeout=1.0

# These are our global objects (and locks for them).
global tx_queue
global tx_lock
global rx_queue
global rx_lock
global spots_lock
global unique
global unique_lock
global s

s=False
tx_queue=Queue()
tx_lock=threading.Lock()
rx_queue=Queue()
rx_lock=threading.Lock()
spots_lock=threading.Lock()
unique_lock=threading.Lock()

# These globals represent the state of JS8Call.
global spots
global dial
global freq
global offset
global grid
global info
global call
global speed
global ptt
global tx_text
global rx_text
global last_rx
global mycall
global messages
global call_activity
global band_activity

spots={}
unique=0

# Note that this assumes US bandplan. TODO: Figure out how to make
# this "locale-friendly" for different countries with different
# bandplans.
def calc_band(freq):
    if(freq>=1800000 and freq<=2000000):
        return("160m")
    elif(freq>=3500000 and freq<=4000000):
        return("80m")
    elif(freq>=5330000 and freq<=5410000):
        return("60m")
    elif(freq>=7000000 and freq<=7300000):
        return("40m")
    elif(freq>=10100000 and freq<=10150000):
        return("30m")
    elif(freq>=14000000 and freq<=14350000):
        return("20m")
    elif(freq>=17068000 and freq<=17168000):
        return("17m")
    elif(freq>=21000000 and freq<=21450000):
        return("15m")
    elif(freq>=24890000 and freq<=24990000):
        return("12m")
    elif(freq>=28000000 and freq<=29700000):
        return("10m")
    elif(freq>=50000000 and freq<=54000000):
        return("6m")
    elif(freq>=144000000 and freq<=148000000):
        return("2m")
    elif(freq>=219000000 and freq<=225000000):
        return("1.25m")
    elif(freq>=420000000 and freq<=450000000):
        return("70cm")
    else:
        return(False)

# Process an incoming message, and record any useful stats about it
# (currently, time, band, grid, speed, snr).
# ToDo: Periodically fetch and parse RX.BAND_ACTIVITY
def process_message(msg):
    global spots
    global spots_lock
    global mycall
    global error
    global messages
    # Process INBOX messages.
    if('MESSAGES' in msg['params']):
        messages=msg['params']['MESSAGES']
    # If it's a SPOT message, we get everything but speed.
    if(msg['type']=="RX.SPOT"):
        with spots_lock:
            band=calc_band(msg['params']['FREQ'])
            if(mycall not in spots):
                spots[mycall]={}
            if(msg['params']['CALL'] not in spots[mycall]):
                spots[mycall][msg['params']['CALL']]=[]
            grid=False
            if(msg['params']['GRID']!=""):
                grid=msg['params']['GRID']
            spots[mycall][msg['params']['CALL']].append({'time':msg['time'],
                                                         'band':band,
                                                         'grid':grid,
                                                         'speed':False,
                                                         'snr':msg['params']['SNR']})
    # If it's a DIRECTED message, we should get everything we hope
    # for, plus maybe some extras, depending on what the CMD is.
    if(msg['type']=="RX.DIRECTED"):
        with spots_lock:
            band=calc_band(msg['params']['FREQ'])
            if(mycall not in spots):
                spots[mycall]={}
            if(msg['params']['FROM'] not in spots[mycall]):
                spots[mycall][msg['params']['FROM']]=[]
            grid=False
            if(msg['params']['GRID']!=""):
                grid=msg['params']['GRID']
            spots[mycall][msg['params']['FROM']].append({'time':msg['time'],
                                                         'band':band,
                                                         'grid':grid,
                                                         'speed':msg['params']['SPEED'],
                                                         'snr':msg['params']['SNR']})
            # If it's an SNR reply, we get to find out how one station
            # hears another, not just how we hear them.
            if(msg['params']['CMD']==" HEARTBEAT SNR" or
                 msg['params']['CMD']==" SNR"):
                grid=False
                if(msg['params']['GRID']!=""):
                    grid=msg['params']['GRID']
                if(msg['params']['FROM'] not in spots):
                    spots[msg['params']['FROM']]={}
                if(msg['params']['TO'] not in spots[msg['params']['FROM']]):
                    spots[msg['params']['FROM']][msg['params']['TO']]=[]
                spots[msg['params']['FROM']][msg['params']['TO']].append({'time':msg['time'],
                                                                          'band':band,
                                                                          'grid':grid,
                                                                          'speed':msg['params']['SPEED'],
                                                                          'snr':int(msg['params']['EXTRA'])})
            # If somebody replies to a GRID? request, capture and save
            # the reply.
            elif(msg['params']['CMD']==" GRID"):
                grid=msg['params']['TEXT'].split()
                band=calc_band(msg['params']['FREQ'])
                if(len(grid)>=4):
                    grid=grid[3]
                    if(not(error in grid)):
                        if(msg['params']['FROM'] not in spots):
                            spots[msg['params']['FROM']]={}
                        if(msg['params']['TO'] not in spots[msg['params']['FROM']]):
                            spots[msg['params']['FROM']][msg['params']['TO']]=[]
                        spots[msg['params']['FROM']][msg['params']['TO']].append({'time':msg['time'],
                                                                                  'band':band,
                                                                                  'grid':grid,
                                                                                  'speed':msg['params']['SPEED'],
                                                                                  'snr':False})
            # If somebody reports who they're hearing, save that.
            elif(msg['params']['CMD']==" HEARING"):
                grid=False
                band=calc_band(msg['params']['FREQ'])
                speed=msg['params']['SPEED']
                if(msg['params']['GRID']!=""):
                    grid=msg['params']['GRID']
                if('FROM' in msg['params']):
                    if(msg['params']['FROM'] not in spots):
                        spots[msg['params']['FROM']]={}
                if(not(error in msg['params']['TEXT'])):
                    hearing=msg['params']['TEXT'].split()[3:-1]
                    for h in hearing:
                        if(h not in msg['params']['FROM']):
                            spots[msg['params']['FROM']][h]=[]
                        spots[msg['params']['FROM']][h].append({'time':msg['time'],
                                                                'band':band,
                                                                'grid':False,
                                                                'speed':speed,
                                                                'snr':False})
#            elif(msg['params']['CMD']==" QUERY CALL"):
#                n=True
#            else:
#                n=True

# Add a message to the outgoing message queue.
def queue_message(message):
    global tx_queue
    global tx_lock
    with tx_lock:
        tx_queue.put(message)

# This thread watches the transmit queue and sends data to JS8
# whenever something appears in the queue.
def tx_thread(name):
    global tx_queue
    global tx_lock
    # Run forever. Delay 0.25 seconds between each send, because
    # sending too quickly jacks up comms with JS8.
    while(True):
        thing=json.dumps(tx_queue.get())
        with tx_lock:
            s.sendall(bytes(thing+"\r\n",'utf-8'))
        time.sleep(0.25)

# Station class for RX.CALL_ACTIVITY
class Callstation:
    def __init__(self,call,stuff):
        self.call=call
        self.snr=stuff['SNR']
        self.utc=stuff['UTC']/1000
        if(stuff['GRID']==''):
            self.grid=False
        else:
            self.grid=stuff['GRID'].strip()

    def age(self):
        return(round(time.time()-self.utc))

    def string(self):
        if(self.grid):
            return('Call: '+self.call+'\tSNR: '+str(self.snr)+'  \tAge: '+str(self.age())+
                  '  \tGrid: '+str(self.grid))
        else:
            return('Call: '+self.call+'\tSNR: '+str(self.snr)+'  \tAge: '+str(self.age()))

# Station class for RX.BAND_ACTIVITY
class Bandstation:
    def __init__(self,stuff):
        self.dial=stuff['DIAL']
        self.freq=stuff['FREQ']
        self.offset=stuff['OFFSET']
        self.snr=stuff['SNR']
        self.text=stuff['TEXT']
        self.utc=stuff['UTC']/1000

    def age(self):
        return(round(time.time()-self.utc))

    def string(self):
        return('Freq: '+str(self.freq/1000)+' khz ('+str(self.dial/1000)+' khz + '+
               str(self.offset)+' hz)  \tSNR: '+str(self.snr)+'  \tAge: '+
               str(self.age())+'  \t Text: '+str(self.text))

# Due to the way JS8Call sends data to an API client (ie, it just
# sends random JSON data whenever it pleases), we'll receive all
# messages in a thread so it'll all work in the background.
def rx_thread(name):
    global spots
    global dial
    global freq
    global offset
    global grid
    global info
    global call
    global speed
    global ptt
    global tx_text
    global rx_text
    global call_activity
    global band_activity
    n=0
    left=False
    empty=True
    # Run forever.
    while(True):
        try:
            # Get a chunk of text and process it. Each valid chunk of
            # data ends in a \n. This is epically painful due to py3's
            # multi-byte characters.
            string=""
            stuff=s.recv(65535)
            if(not(empty)):
                stuff=left+stuff
            if(stuff[0:1]==b'{' and stuff[-2:-1]==b'}'):
                string=stuff.decode("utf-8")
                empty=True
            else:
              if(empty):
                  empty=False
                  left=stuff
            if(string==""):
                message={"type":"empty"}
            else:
                string=string.rstrip("\n")
                for m in string.split("\n"):
                    message=json.loads(m)
                    now=time.time()
                    message['time']=now
                    last_rx=now
                    # If the message contains something we need to
                    # process (for example, the result of a frequency
                    # query), do it. If it's just incoming text, queue
                    # it for the user.
                    if('params' in list(message.keys())):
                        if('TEXT' in list(message['params'].keys())):
                            if(error in message['params']['TEXT']):
                                message['rxerror']=True
                            else:
                                message['rxerror']=False
                    processed=False
                    try:
                        process_message(message)
                    except Exception:
                        print("Message: ",message)
                        traceback.print_exc()
                    if(message['type']=="RIG.FREQ"):
                        processed=True
                        dial=message['params']['DIAL']
                        freq=message['params']['FREQ']
                        offset=message['params']['OFFSET']
                    elif(message['type']=="STATION.CALLSIGN"):
                        processed=True
                        call=message['value']
                    elif(message['type']=="STATION.GRID"):
                        processed=True
                        grid=message['value']
                    elif(message['type']=="STATION.INFO"):
                        processed=True
                        info=message['value']
                    elif(message['type']=="MODE.SPEED"):
                        processed=True
                        speed=str(message['params']['SPEED'])
                    elif(message['type']=="RIG.PTT"):
                        processed=True
                        if(message['value'])=="on":
                           ptt=True
                        else:
                           ptt=False
                    elif(message['type']=="RX.CALL_SELECTED"):
                        processed=True
                    elif(message['type']=="TX.FRAME"):
                        processed=True
                    elif(message['type']=="TX.TEXT"):
                        processed=True
                        tx_text=message['value']
                    elif(message['type']=="RX.TEXT"):
                        # Note that we don't mark this as 'processed'
                        # (even though it is), as the user may want to
                        # watch for incoming text to take his own
                        # action.
                        rx_text=message['value']
                    elif(message['type']=="RX.CALL_ACTIVITY"):
                        processed=True
                        tmp=message['params']
                        if('_ID' in tmp):
                            del(tmp['_ID'])
                        stations=list(map(lambda c: Callstation(c,tmp[c]),list(tmp.keys())))
                        call_activity=stations
                    elif(message['type']=="RX.BAND_ACTIVITY"):
                        processed=True
                        tmp=message['params']
                        if('_ID' in tmp):
                            del(tmp['_ID'])
                        stations=list(map(lambda c: Bandstation(tmp[c]),list(tmp.keys())))
                        band_activity=stations
                    elif(message['type']=="RX.SPOT"):
                        processed=True
                    # The following message types are delivered to the
                    # rx_queue for user processing (though some of
                    # them are also internally processed):
                    # RX.DIRECTED, RX.ACTIVITY, RX.SPOT,
                    # RX.BAND_ACTIVITY, RX.TEXT. If any other messages
                    # show up in the queue, it's a bug.
                    if(not(processed)):
                        with rx_lock:
                           rx_queue.put(message)
            time.sleep(0.1)
        except socket.timeout:
        # Ignore for now. TODO: Be smarter here.
            n=n+1
            time.sleep(0.1)

# This thread makes sure the connection is alive by sending a
# heartbeat request (specifically, a request for callsign) every five
# minutes.
def hb_thread(name):
    # Run forever. Sleep five minutes between runs.
    global mycall
    while(True):
        mycall=get_callsign()
        time.sleep(300)

def start_net(host,port):
    global s

    # Open a socket to JS8Call.
    s=socket.socket()
    s.connect((host,int(port)))
    s.settimeout(1)

    # Start the RX thread. We make this a daemon thread so that it
    # will automatically die when the main thread dies. Kind of dirty,
    # but there's no risk of data loss, and the OS will automatically
    # take care of the socket clean-up when the process exits.
    thread1=Thread(target=rx_thread,args=("RX Thread",),daemon=True)
    thread1.start()
    # Start the TX thread. Also a daemon thread.
    thread2=Thread(target=tx_thread,args=("TX Thread",),daemon=True)
    thread2.start()
    # Start the heartbeat thread. Also a daemon thread.
    thread3=Thread(target=hb_thread,args=("HB Thread",),daemon=True)
    thread3.start()
    time.sleep(1)

def get_freq():
    # Ask JS8Call to get the radio's frequency. Returns the dial
    # frequency (in hz), the offset in the audio passband (in hz), and
    # the actual effective transmit frequency (basically the two
    # values added together) as a JSON blob.
    global dial
    global freq
    global offset
    global timeout
    dial=False
    freq=False
    offset=False
    queue_message({"params":{},"type":"RIG.GET_FREQ","value":""})
    now=time.time()
    while(not(dial) or not(freq) or not(offset)):
        if(time.time()>now+timeout):
            return(False)
        time.sleep(0.1)
    return({"dial":dial,"freq":freq,"offset":offset})

def set_freq(dial,offset):
    # Set the radio's dial freq (in hz) and the offset within the
    # passband (also in hz).
    queue_message({"params":{"DIAL":dial,"OFFSET":offset},"type":"RIG.SET_FREQ","value":""})
    time.sleep(0.1)
    return(get_freq())

def get_messages():
    # Fetch all inbox messages.
    queue_message({"params":{},"type":"INBOX.GET_MESSAGES","value":""})
    global messages
    global timeout
    messages=False
    now=time.time()
    while(not(messages)):
        if(time.time()>now+timeout):
            return(False)
        time.sleep(0.1)
    return(messages)

def store_message(callsign,text):
    # Store a message in the INBOX for later pickup by recipient.
    queue_message({"params":{"CALLSIGN":callsign,"TEXT":text},"type":"INBOX.STORE_MESSAGE","value":""})
    time.sleep(0.1)
    return(get_messages())

def get_callsign():
    # Ask JS8Call for the configured callsign.
    global call
    global timeout
    call=False
    queue_message({"params":{},"type":"STATION.GET_CALLSIGN","value":""})
    now=time.time()
    while(not(call)):
        if(time.time()>now+timeout):
            return(False)
        time.sleep(0.1)
    return(call)

def get_grid():
    # Ask JS8Call for the configured grid square.
    global grid
    global timeout
    grid=False
    queue_message({'params':{},'type':'STATION.GET_GRID','value':''})
    now=time.time()
    while(not(grid)):
        if(time.time()>now+timeout):
            return(False)
        time.sleep(0.1)
    return(grid)

def set_grid(grid):
    # Set the grid square.
    queue_message({"params":{},"type":"STATION.SET_GRID","value":grid})
    return(get_grid())

def send_aprs_grid(grid):
    # Send the supplied grid info to APRS (use
    # send_aprs_grid(get_grid()) to send your configured grid square).
    send_message("@APRSIS GRID "+grid)

def send_heartbeat(grid=False):
    # Send a heartbeat message.
    if(not(grid)):
        grid=get_grid()
    if(len(grid)>=4):
        grid=grid[0:4]
        send_message(get_callsign()+": @HB HEARTBEAT "+grid)

def send_sms(phone,message):
    # Send an SMS message via JS8.
    global unique
    global unique_lock
    with unique_lock:
        unique=unique+1
        if(unique>99):
            unique=1
        send_message("@APRSIS CMD :SMSGTE   :@"+phone+" "+message+"{%02d}" % unique)

def send_email(address,message):
    # Send an email message via JS8.
    global unique
    global unique_lock
    with unique_lock:
        unique=unique+1
        if(unique>99):
            unique=1
        send_message("@APRSIS CMD :EMAIL-2  :"+address+" "+message+"{%02d}" % unique)

def send_aprs(dest,message):
    # Send an APRS message to the destination call. Your call is sent
    # as configured in JS8Call. Be reasonable with the message
    # length. I'm not certain what the length limit in APRS is, but
    # there almost certainly is one.
    global unique
    global unique_lock
    dest=dest[0:9]
    while(len(dest)<9):
        dest=dest+" "
    with unique_lock:
        unique=unique+1
        if(unique>99):
            unique=1
        send_message("@APRSIS CMD :"+dest+":"+message+"{%02d}" % unique)

def send_sota(summit,freq,mode,comment=False):
    # Send a SOTA spot. freq is an integer in khz (ie, 7200, 14300,
    # 144200).  Your call is sent as configured in JS8Call. Don't get
    # too creative with the mode. Stick with the basics: USB, LSB,
    # SSB, AM, FM, CW, etc, lest your message get dropped.. You must
    # pre-register with the SOTA gateway for this to work:
    # https://www.sotaspots.co.uk/Aprs2Sota_Info.php
    global unique
    global unique_lock
    with unique_lock:
        unique=unique+1
        if(unique>99):
            unique=1
        if(comment):
            send_message("@APRSIS CMD :APRS2SOTA:"+get_callsign()+";"+summit+";"+str(int(freq))+";"+mode+";"+comment+"{%02d}" % unique)
        else:
            send_message("@APRSIS CMD :APRS2SOTA:"+get_callsign()+";"+summit+";"+str(int(freq))+";"+mode+"{%02d}" % unique)

def send_pota(park,freq,mode,comment=False):
    # Send a POTA spot. freq is an integer in khz (ie, 7200, 14300,
    # 144200).  Your call is sent as configured in JS8Call.
    global unique
    global unique_lock
    with unique_lock:
        unique=unique+1
        if(unique>99):
            unique=1
        if(comment):
            send_message("@APRSIS CMD :POTAGW   :"+get_callsign()+" "+park+" "+str(int(freq))+" "+mode+" "+comment+"{%02d}" % unique)
        else:
            send_message("@APRSIS CMD :POTAGW   :"+get_callsign()+" "+park+" "+str(int(freq))+" "+mode+"{%02d}" % unique)

def get_info():
    # Ask JS8Call for the configured info field.
    global info
    global timeout
    info=False
    queue_message({"params":{},"type":"STATION.GET_INFO","value":""})
    now=time.time()
    while(not(info)):
        if(time.time()>now+timeout):
            return(False)
        time.sleep(0.1)
    return(info)

def set_info(info):
    # Set the info field.
    queue_message({"params":{},"type":"STATION.SET_INFO","value":info})
    return(get_info())

def get_call_activity():
    # Get the contents of the right white window.
    global call_activity
    call_activity=False
    queue_message({"params":{},"type":"RX.GET_CALL_ACTIVITY","value":""})
    now=time.time()
    while(not(call_activity)):
        if(time.time()>now+timeout):
            return(False)
        time.sleep(0.1)
    return(call_activity)

def get_call_selected():
    # Never quite figured out what this does. I assume based on the
    # name that it returns the value of whichever callsign has been
    # clicked on in the right window, but I haven't gotten 'round to
    # testing this theory. ToDo: figure this out
    queue_message({"params":{},"type":"RX.GET_CALL_SELECTED","value":""})

def get_band_activity():
    # Get the contents of the left white window.
    global band_activity
    band_activity=False
    queue_message({"params":{},"type":"RX.GET_BAND_ACTIVITY","value":""})
    now=time.time()
    while(not(band_activity)):
        if(time.time()>now+timeout):
            return(False)
        time.sleep(0.1)
    return(band_activity)

def get_rx_text():
    # Get the contents of the yellow window.
    global rx_text
    global timeout
    rx_text='-=-=-=-shibboleeth-=-=-=-'
    queue_message({"params":{},"type":"RX.GET_TEXT","value":""})
    now=time.time()
    while(rx_text=='-=-=-=-shibboleeth-=-=-=-'):
        if(time.time()>now+timeout):
            return(False)
        time.sleep(0.1)
    return(rx_text)
    
def get_tx_text():
    # Get the contents of the window below yellow window.
    global tx_text
    global timeout
    tx_text='-=-=-=-shibboleeth-=-=-=-'
    queue_message({"params":{},"type":"TX.GET_TEXT","value":""})
    now=time.time()
    while(tx_text=='-=-=-=-shibboleeth-=-=-=-'):
        if(time.time()>now+timeout):
            return(False)
        time.sleep(0.1)
    return(tx_text)

def set_tx_text(text):
    # Set the contents of the window below yellow window.
    global tx_text
    queue_message({"params":{},"type":"TX.SET_TEXT","value":text})
    return(get_tx_text())

def get_speed():
    # Ask JS8Call what speed it's currently configured for.
    # slow==4, normal==0, fast==1, turbo==2
    global speed
    global timeout
    speed=False
    queue_message({"params":{},"type":"MODE.GET_SPEED","value":""})
    now=time.time()
    while(not(speed)):
        if(time.time()>now+timeout):
            return(False)
        time.sleep(0.1)
    return(speed)
    
def speed_name(speed):
    if(speed>=0 and speed<=4):
        return(['Normal', 'Fast', 'Turbo', 'Invalid', 'Slow'][speed])
    else:
        return('Invalid')

def set_speed(speed):
    # Set the JS8Call transmission speed.
    # slow==4, normal==0, fast==1, turbo==2
    queue_message({"params":{"SPEED":speed},"type":"MODE.SET_SPEED","value":""})
    return(get_speed())

def raise_window():
    # Raise the JS8Call window to the top.
    queue_message({"params":{},"type":"WINDOW.RAISE","value":""})

def send_message(message):
    # Send 'message' in the next transmit cycle.
    queue_message({"params":{},"type":"TX.SEND_MESSAGE","value":message})

def send_directed_message(dest_call,message):
    # Send directed 'message' (to a specific call sign) in the next
    # transmit cycle.
    queue_message({"params":{},"type":"TX.SEND_MESSAGE","value":dest_call+" "+message})

def send_inbox_message(dest_call,message):
    # Send directed 'message' (to a specific call sign) in the next
    # transmit cycle.
    queue_message({"params":{},"type":"TX.SEND_MESSAGE","value":dest_call+" MSG "+message})

def alive():
    # Return true if the TCP connection appears to still be alive (ie,
    # a valid response was received in the last five minutes + wiggle
    # room). Else return false. It's up to you to re-establish comms
    # if the connection has failed.
    global last_rx
    if(time.time()-last_rx<=335):
        return(true)
    else:
        return(false)
    
def query_snr(dest_call):
    # Query a station for your SNR report.
    queue_message({"params":{},"type":"TX.SEND_MESSAGE","value":dest_call+" SNR? "})

def query_grid(dest_call):
    # Query a station for their grid square.
    queue_message({"params":{},"type":"TX.SEND_MESSAGE","value":dest_call+" GRID? "})

def query_status(dest_call):
    # Query a station for their status.
    queue_message({"params":{},"type":"TX.SEND_MESSAGE","value":dest_call+" STATUS? "})

def query_info(dest_call):
    # Query a station for their info.
    queue_message({"params":{},"type":"TX.SEND_MESSAGE","value":dest_call+" INFO? "})

def query_hearing(dest_call):
    # Query a station for top stations heard.
    queue_message({"params":{},"type":"TX.SEND_MESSAGE","value":dest_call+" HEARING? "})

if __name__ == '__main__':
    print("This is a library and is not intended for stand-alone execution.")

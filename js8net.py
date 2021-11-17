#!/usr/bin/env python3
# coding: utf-8

import sys
import socket
import json
import time
import threading
from threading import Thread
from queue import Queue

# Defaults within JS8Call.
eom="♢"
error="…"

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
global text

spots={}
unique=0

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
    global text
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
                    message['time']=time.time()
                    # If the message contains something we need to
                    # process (for example, the result of a frequency
                    # query), do it. If it's just incoming text, queue
                    # it for the user.
                    processed=False
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
                        text=message['value']
                    elif(message['type']=="RX.TEXT"):
                        # Note that we don't mark this as 'processed'
                        # (even though it is), as the user may want to
                        # watch for incoming text to take his own
                        # action.
                        text=message['value']
                    elif(message['type']=="RX.SPOT"):
                        # Note that we don't mark this as 'processed'
                        # (even though it is), as the user may want to
                        # watch for incoming spots to take his own
                        # action.
                        with spots_lock:
                           if(message['params']['CALL'] not in spots):
                               spots[message['params']['CALL']]=[]
                           spots[message['params']['CALL']].append(message)
                    # The following message types are delivered to the
                    # rx_queue for user processing (though some of
                    # them are also internally processed):
                    # RX.DIRECTED, RX.ACTIVITY, RX.SPOT,
                    # RX.CALL_ACTIVITY, RX.GET_BAND_ACTIVITY,
                    # RX.TEXT. If any other messages show up in the
                    # queue, it's a bug.
                    if(not(processed)):
                        with rx_lock:
                           rx_queue.put(message)
            time.sleep(0.1)
        except socket.timeout:
        # Ignore for now. TODO: Be smarter here.
            n=n+1
            time.sleep(0.1)

def start_net(host,port):
    global s

    # Open a socket to JS8Call.
    s=socket.socket()
    s.connect((host,port))
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

def get_freq():
    # Ask JS8Call to get the radio's dial frequency.
    global dial
    global freq
    global offset
    dial=False
    freq=False
    offset=False
    queue_message({"params":{},"type":"RIG.GET_FREQ","value":""})
    while(not(dial) or not(freq) or not(offset)):
        time.sleep(0.1)
    return({"dial":dial,"freq":freq,"offset":offset})

def set_freq(dial,offset):
    queue_message({"params":{"DIAL":dial,"OFFSET":offset},"type":"RIG.SET_FREQ","value":""})
    time.sleep(0.1)
    return(get_freq())

def get_callsign():
    # Ask JS8Call for the configured callsign.
    global call
    call=False
    queue_message({"params":{},"type":"STATION.GET_CALLSIGN","value":""})
    while(not(call)):
        time.sleep(0.1)
    return(call)

def get_grid():
    # Ask JS8Call for the configured grid square.
    global grid
    grid=False
    queue_message({'params':{},'type':'STATION.GET_GRID','value':''})
    while(not(grid)):
        time.sleep(0.1)
    return(grid)

def set_grid(grid):
    queue_message({"params":{},"type":"STATION.SET_GRID","value":grid})
    return(get_grid())

def send_aprs_grid(grid):
    send_message("@APRSIS GRID "+grid)

def send_sms(phone,message):
    with unique_lock:
        unique=unique+1
        send_message("#APRSIS CMD :SMSGTE  :@"+phone+" "+message+"{%03d}" % unique)

def send_email(address,message):
    with unique_lock:
        unique=unique+1
        send_message("#APRSIS CMD :EMAIL-2  :"+address+" "+message+"{%03d}" % unique)

def get_info():
    # Ask JS8Call for the configured info field.
    global info
    info=False
    queue_message({"params":{},"type":"STATION.GET_INFO","value":""})
    while(not(info)):
        time.sleep(0.1)
    return(info)

def set_info(info):
    queue_message({"params":{},"type":"STATION.SET_INFO","value":info})
    return(get_info())

def get_call_activity():
    # Get the contents of the right white box.
    queue_message({"params":{},"type":"RX.GET_CALL_ACTIVITY","value":""})

def get_call_selected():
    queue_message({"params":{},"type":"RX.GET_CALL_SELECTED","value":""})

def get_band_activity():
    # Get the contents of the left white box.
    queue_message({"params":{},"type":"RX.GET_BAND_ACTIVITY","value":""})

def get_rx_text():
    # Get the contents of the yellow window.
    global text
    text='-=-=-=-shibboleeth-=-=-=-'
    queue_message({"params":{},"type":"RX.GET_TEXT","value":""})
    while(text=='-=-=-=-shibboleeth-=-=-=-'):
        time.sleep(0.1)
    return(text)
    
def get_tx_text():
    # Get the contents of the box below yellow window.
    global text
    text='-=-=-=-shibboleeth-=-=-=-'
    queue_message({"params":{},"type":"TX.GET_TEXT","value":""})
    while(text=='-=-=-=-shibboleeth-=-=-=-'):
        time.sleep(0.1)
    return(text)

def get_speed():
    # Ask JS8Call what speed it's currently configured for.
    # slow==4, normal==0, fast==1, turbo==2
    global speed
    speed=False
    queue_message({"params":{},"type":"MODE.GET_SPEED","value":""})
    while(not(speed)):
        time.sleep(0.1)
    return(speed)
    
def raise_window():
    # Raise the JS8Call window to the top.
    queue_message({"params":{},"type":"WINDOW.RAISE","value":""})

def send_message(message):
    # Send 'message' in the next transmit cycle.
    queue_message({"params":{},"type":"TX.SEND_MESSAGE","value":message})

if __name__ == '__main__':
    print("This is a library and is not intended for stand-alone execution.")

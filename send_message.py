#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import time
import argparse
from js8net import *

# Main program.
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Send a directed message via JS8Call.")
    parser.add_argument("--js8_host",default=False,help="IP/DNS of JS8Call server (default localhost, env: JS8HOST)")
    parser.add_argument("--js8_port",default=False,help="TCP port of JS8Call server (default 2442, env: JS8PORT)")
    parser.add_argument("--call",default=False,help="Specify recipient call sign")
    parser.add_argument("--msg",default=False,help="Message to send")
    parser.add_argument("--ack",default=False,help="How long to Wait for ACK (seconds, includes TX time, 180 is reasonable here, for moderate messages)")
    parser.add_argument("--snr",default=False,action="store_true",help="Try SNR? first")
    parser.add_argument("--freq",default=False,help="Specify transmit freq (hz, ex: 7079000)")
    parser.add_argument("--freq_dial",default=False,help="Specify dial freq (hz, ex: 7078000)")
    parser.add_argument("--freq_audio",default=False,help="Specify transmit offset freq (hz, ex: 1000)")
    parser.add_argument("--speed",default=False,help="Specify transmit speed (slow==4, normal==0, fast==1, turbo==2)")
    parser.add_argument("--env",default=False,action="store_true",help="Use environment variables (cli options override)")
    parser.add_argument("--verbose",default=False,action="store_true",help="Lots of status messages")
    args=parser.parse_args()

    js8host=False
    js8port=False

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

    if(not(args.msg and args.call)):
        print("--msg and --addr are mandatory")
    else:
        if(args.verbose):
            print("Connecting to JS8Call...")
        start_net(js8host,js8port)
        if(args.verbose):
            print("Connected.")
        if(args.freq or args.freq_dial or args.freq_audio):
            f=get_freq()
            if(args.freq_dial and args.freq_audio):
                set_freq(args.freq_dial,args.freq_audio)
            elif(args.freq and args.freq_audio):
                set_freq(args.freq_dial-args.freq_audio,args.freq_audio)
            elif(args.freq):
                set_freq(args.freq_dial-1000,1000)
            elif(args.freq_audio):
                set_freq(f['dial'],args.freq_audio)
        if(args.verbose):
            print("Frequency set to ",get_freq())
        if(args.speed):
            speed=int(args.speed)
            if(speed>=0 and speed<=4 and speed!=3):
                if(args.verbose):
                    print("Setting speed to ",str(speed))
                set_speed(speed)
        snr=False
        if(not(args.snr)):
            snr=True
        else:
            if(args.verbose):
                print("Asking "+args.call+" for SNR...")
            send_message(args.call+" SNR?")
            now=time.time()
            # ToDo: This should be calculated based on *HIS* speed,
            # not *MY* speed. In theory, we have that from the SNR?
            # reply. Just need to save it for use here. This, of
            # course, assumes he doesn't change speed mid-stream
            # (which is unlikely, but not impossible).
            speed=get_speed()
            done=False
            if(speed==0):
                done=now+int(15*2.5)
            elif(speed==1):
                done=now+int(10*2.5)
            elif(speed==2):
                done=now+int(6*2.5)
            elif(speed==4):
                done=now+int(30*2.5)
            mycall=get_callsign()
            while(done>time.time()):
                time.sleep(1)
                if(not(rx_queue.empty())):
                    with rx_lock:
                        rx=rx_queue.get()
                        if(rx['type']=="RX.DIRECTED"):
                            if(rx['params']['CMD']==" SNR" and
                               rx['params']['FROM']==args.call and
                               rx['params']['TO']==mycall):
                                snr=True
                                done=time.time()
                                if(args.verbose):
                                    print("Successfully received SNR: ",str(rx['params']['EXTRA']))

        if(not(snr)):
            if(args.verbose):
                print("Failed to receive ACK.")
            sys.exit(2)
        else:
            send_inbox_message(args.call,args.msg)
            time.sleep(3)
            if(args.verbose):
                print("Message sent.")
            if(args.ack):
                if(args.verbose):
                    print("Awaiting ACK...")
                now=time.time()
                done=now+int(args.ack)
                mycall=get_callsign()
                while(done>time.time()):
                    time.sleep(1)
                    if(not(rx_queue.empty())):
                        with rx_lock:
                            rx=rx_queue.get()
                            if(rx['type']=="RX.DIRECTED"):
                                if(rx['params']['CMD']==" ACK" and
                                   rx['params']['FROM']==args.call and
                                   rx['params']['TO']==mycall):
                                    if(args.verbose):
                                        print("Successfully received ACK.")
                                    sys.exit(0)
                if(args.verbose):
                    print("Failed to receive ACK.")
                sys.exit(1)

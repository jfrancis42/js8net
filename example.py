#!/usr/bin/env python3
# coding: utf-8

import sys
import time
from js8net import *

# Main program.
if __name__ == '__main__':
    start_net("10.1.1.141",2442)
    time.sleep(1)
    print("Call: ",get_callsign())
    print("Grid: ",get_grid())
    print("Info: ",get_info())
    print("Freq: ",get_freq())
    print("Speed: ",get_speed())
#    print(get_tx_text())
#    print(get_rx_text())
    print("Freq: ",set_freq(7078000,2000))
    get_band_activity()
    
    while(True):
        if(not(rx_queue.empty())):
            print(rx_queue.get())

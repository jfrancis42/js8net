#!/usr/bin/env python3
# coding: utf-8

import sys
import time
from js8net import *

# Main program.
if __name__ == '__main__':
    start_net("10.1.1.141",2442)
    time.sleep(1)
    print(get_callsign())
    print(get_grid())
    print(get_info())
    print(get_freq())
    print(get_speed())
#    print(get_tx_text())
#    print(get_rx_text())
    print(set_freq(7078000,2000))
    
    while(True):
        if(not(rx_queue.empty())):
            print(rx_queue.get())

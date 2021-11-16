#!/usr/bin/env python
# coding: utf-8

import sys
import time
from js8net import *

# Main program.
if __name__ == '__main__':
    start_net("10.1.1.141",2442)
    time.sleep(1)
    print(get_grid())
    print(get_info())
    print(get_freq())
    

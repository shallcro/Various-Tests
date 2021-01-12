#!/usr/bin/env python3

import os
import sys
import tkinter as tk

# from dfxml project
import Objects

def close_app(window):
    window.destroy()
    sys.exit(0)

def newscreen():
    os.system('cls')

    fname = "C:/BDPL/scripts/bdpl.txt"
    if os.path.exists(fname):
        with open(fname, 'r') as fin:
            print(fin.read())
            print('\n')
    else:
        print('Missing ASCII art header file; download to: {}'.format(fname))
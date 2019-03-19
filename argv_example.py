#!/usr/bin/python3

import sys

""" An example of how to read variables """

def help():
    print ("""
    This is a simple script, to make it run you just need to:
    1) ./argv_example.py first second third
    
    Otherwise it is not going to work
    """)

try:
    script, first, second, third = argv
except:
    help()
    sys.exit()
print ("Script: ", script)
print ("First: ", first)
print ("Second: ", second)
print ("Third: ", third)

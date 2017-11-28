#!/usr/bin/env python3

#import libnmap
#import nmap
import json
import subprocess
import os

from threading import Timer

subprocess.call(['airmon-ng', 'check', 'kill'], stdout=subprocess.PIPE)
subprocess.call(['ifconfig', 'eth0', 'down'], stdout=subprocess.PIPE)
subprocess.call(['airmon-ng', 'start', 'wlan1'], stdout=subprocess.PIPE)

kill = lambda process: process.kill()
cmd = ['airodump-ng', '-c', '1', '-a', 'wlan1mon']
network_discovery = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
my_timer = Timer(5, kill, [network_discovery])
try:
    my_timer.start()
    stdout, stderr = network_discovery.communicate()
    print(stdout)
finally:
    my_timer.cancel()

#run airodump for single channel, then timeout

#read testcap-01 files and parse data

#store data to JSON output file

###########################################
#reading data from file sample
#import csv

#file = csv.reader(open('testcap-01.csv', newline=''), delimiter=' ',quotechar='|')
#for row in file:
#	print(','.join(row))


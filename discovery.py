#!/usr/bin/env python3

#import libnmap
#import nmap
import json
import subprocess
from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException
import subprocess

class Target:

	def __init__(self, ip, mac, name=None):
		self.name = name
		self.ip = ip
		self.mac = mac

	def __repr__(self):
		return "Target(" + ", ".join(filter(None, [self.name, self.ip, self.mac])) + ")"

def arp_scan():
    scan_results = subprocess.run(["arp-scan", "--localnet"], stdout=subprocess.PIPE)
    output = scan_results.stdout.decode("utf-8")

    arp_table = {}
    for line in output.splitlines():
        data = line.split('\t')
        if len(data) == 3:
            ip, mac, name = data
            arp_table[ip] = Target(ip, mac)

    return arp_table


def get_device_names(arp_table):
    targets = list(arp_table.keys())

    for i in range(3):
	    nmproc = NmapProcess(targets, "-sn")
	    nmproc.run()

	    try:
	        nmap_report = NmapParser.parse(nmproc.stdout)
	        
	        for host in nmap_report.hosts:
	        	if host.hostnames:
	        		arp_table[host.address].name = host.hostnames[0]
	    except NmapParserException:
	        pass
	
    return arp_table

if __name__ == "__main__":
	arp_table = arp_scan()
	print(get_device_names(arp_table))
#!/usr/bin/env python3

#import libnmap
#import nmap
import json
import subprocess
from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException
import subprocess

class Target:

    def __init__(self, mac, ip=None, name=None):
        self.name = name
        self.ip = ip
        self.mac = mac

    def __repr__(self):
        return "Target" + str(self)

    def __str__(self):
        return "(" + ", ".join(filter(None, [self.name, self.ip, self.mac])) + ")"

def arp_scan():
    scan_results = subprocess.run(["arp-scan", "--localnet"], stdout=subprocess.PIPE)
    output = scan_results.stdout.decode("utf-8")

    arp_table = {}
    for line in output.splitlines():
        data = line.split('\t')
        if len(data) == 3:
            ip, mac, name = data
            mac = mac.upper()
            target = Target(mac, ip)
            arp_table[ip] = target
            arp_table[mac] = target

    return arp_table


def get_hostnames(arp_table):
    targets = list(arp_table.keys())

    for i in range(3):
        nmproc = NmapProcess(targets, "-sn")
        nmproc.run()

        try:
            nmap_report = NmapParser.parse(nmproc.stdout)

            for host in nmap_report.hosts:
                if host.hostnames:
                    name = host.hostnames[0]
                    arp_table[host.address].name = name
                    arp_table[name] = arp_table[host.address]
        except NmapParserException:
            pass
	
    return arp_table

if __name__ == "__main__":
    arp_table = arp_scan()
    arp_table = get_hostnames(arp_table)
    print(arp_table)

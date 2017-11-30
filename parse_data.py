import csv
import json

"""
	DICTIONARY 1 FORMAT

	essid_data {
		ESSID {
			channels {
				BSSID {
					Client1 mac
						device name
						optional data
						...
					Client2 mac
						device name
						optional data
						...
					...
				}
			}
		}
	}

	DICTIONARY 2 FORMAT

	essid_data {
		Client1 mac {
			Device name
			optional data
			...
			BSSIDS {
				BSSID 1 {
					Channel {
						ESSID
					}
				}

				BSSID 2 {
					...
				}
			}
		}
	}

"""
essid_data = {}
client_data = {}

with open('testcap-01.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, skipinitialspace=True)

	bssid_to_essid_and_channel = {}

	# first empty row denotes the start of the access points table
	# second empty row denotes the start of the stations table
	table_num = 0
	skip_row = False
	for row in reader:
		if not row:
			table_num += 1
			skip_row = True
			continue
		if skip_row:
			skip_row = False
			continue

		if table_num == 1:
			bssid = row[0].strip()
			channel = row[3].strip()
			essid = row[13].strip()

			bssid_to_essid_and_channel[bssid] = (essid, channel)

			if essid in essid_data.keys():
				if channel in essid_data[essid].keys():
					essid_data[essid][channel][bssid] = {}
					continue
				bssid_dict = {}
				bssid_dict[bssid] = {}
				essid_data[essid][channel] =  bssid_dict
			else:
				bssid_dict = {}
				bssid_dict[bssid] = {}
				channel_dict = {}
				channel_dict[channel] = bssid_dict

				essid_data[essid] = channel_dict

		elif table_num == 2:
			mac = row[0].strip()
			bssid = row[5].strip()
			#probed_essid = row[6].strip()

			if bssid == '(not associated)':
				continue

			essid, channel = bssid_to_essid_and_channel[bssid]

			mac_data = {}
			mac_data['device name'] = ''
			mac_data['operating system'] = ''
			mac_data['ports'] = []

			essid_data[essid][channel][bssid][mac] = mac_data

print(json.dumps(essid_data, indent=4))

# Create dictionary 2 from dictionary 1
for essid, channels in essid_data.items():
	for channel, bssids in channels.items():
		for bssid, clients in bssids.items():
			for client_mac, mac_data in clients.items():
				if client_mac not in client_data:
					client_data[client_mac] = dict(mac_data)
					client_data[client_mac]['bssids'] = {}
				bssid_data = client_data[client_mac]['bssids']
				if bssid not in bssid_data:
					bssid_data[bssid] = {}
				bssid_data[bssid][channel] = essid

print(json.dumps(client_data, indent=4))
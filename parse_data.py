import csv
import json

with open('testcap-01.csv', newline='') as csvfile:
	reader = csv.reader(csvfile)

	"""
		dictionary 1 format

		victims {
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
	"""
	victims = {}
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
			essid = row[13]

			bssid_to_essid_and_channel[bssid] = (essid, channel)

			if essid in victims.keys():
				if channel in victims[essid].keys():
					victims[essid][channel][bssid] = {}
					continue
				bssid_dict = {}
				bssid_dict[bssid] = {}
				victims[essid][channel] =  bssid_dict
			else:
				bssid_dict = {}
				bssid_dict[bssid] = {}
				channel_dict = {}
				channel_dict[channel] = bssid_dict
				
				victims[essid] = channel_dict

		elif table_num == 2:
			mac = row[0].strip()
			bssid = row[5].strip()
			probed_essid = row[6]

			if bssid == '(not associated)':
				continue

			essid, channel = bssid_to_essid_and_channel[bssid]

			mac_dict = {}
			mac_dict['device name'] = probed_essid
			mac_dict['operating system'] = ''
			mac_dict['ports'] = []
			victims[essid][channel][bssid] = mac_dict

	print(json.dumps(victims, indent=4))
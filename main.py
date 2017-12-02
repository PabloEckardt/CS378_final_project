import argparse
import re
import subprocess
import sys

import parse_data


_mac_address_pattern = re.compile('[0-9A-F]{2}(:[0-9A-F]{2}){5}')

def mac_address_or_all(addr):
    if addr.lower() == 'all':
        return 'all'
    return mac_address(addr)


def mac_address(addr):
    """ mac_address checks that a given string is in MAC address format """
    mac = addr.upper()
    if not _mac_address_pattern.fullmatch(mac):
        raise TypeError('{} does not match a MAC address pattern'.format(addr))
    return mac


def ip_address(addr):
    """ ip_address checks that a given string is in IP address format """
    parts = addr.split('.')
    if len(parts) != 4:
        raise TypeError('{} does not match an IP address pattern'.format(addr))
    for part in parts:
        try:
            num = int(part)
            if num < 0 or num > 255:
                raise TypeError('{} does not match an IP address pattern'.format(addr))
        except ValueError:
            raise TypeError('{} does not match an IP address pattern'.format(addr))
    return addr


def parse_args():
    parser = argparse.ArgumentParser(description='Deauthenticate targets from a wifi network.')
    
    subparsers = parser.add_subparsers(title="actions", description='valid actions (no action means to deauth a set of targets)', dest='action')
    deauth_parser = subparsers.add_parser('deauth', help='deauth some set of targets from specified networks')
    deauth_parser.add_argument('target', nargs='+', type=mac_address_or_all, help='the MAC addresses to deauth (use "all" to target everything)')

    network_group = deauth_parser.add_argument_group('network', 'specify the access points to deauth from (required)')
    network_group.add_argument('-B', '--bssids', action='append', type=mac_address, help='the BSSIDs of the networks to send deauth packets to')
    network_group.add_argument('-n', '--network-names', '-E', '--essids', '-S', '--ssids', action='append', help='the names of the networks to send deauth packets to', dest='network_names')

    bully_parser = subparsers.add_parser('bully', help='deauth a target from all networks')
    bully_parser.add_argument('target', type=mac_address, help='the MAC address to deauth')

    discover_parser = subparsers.add_parser('discover', help='locate targets to deauth')

    args = parser.parse_args()
    if args.action is None:
        parser.print_help()
        sys.exit(0)
    if args.action == 'deauth' and not args.bssids and not args.network_names:
        print('Please specify a network to deauth from', file=sys.stderr)
        parser.print_usage(file=sys.stderr)
        sys.exit(1)
    return args


def discover_network(args=None):
    """
    discovery_results = subprocess.run(['discovery.sh'], stderr=subprocess.PIPE, encoding='utf-8')
    if discovery_results.returncode != 0:
        print(discovery_results.stderr, file=sys.stderr)
        sys.exit(1)
    """
    essid_data = parse_data.parse_network_packets(parse_data.get_file_name())
    if args is not None:
        # if args are passed in, then we need to print the data
        parse_data.display_json(essid_data)
        return
    inverted_index = parse_data.invert_index(essid_data)
    return essid_data, inverted_index


def deauth_clients(args):
    # targets to deauth
    target_all = 'all' in args.target
    targets = [] if target_all else [t for t in args.target if t != 'all']

    # networks to send deauth packets too
    bssids = args.bssids or [] # list of BSSID MAC addresses
    network_names = args.network_names or [] # list of string network names or None

    essid_data, inverted_index = discover_network()

    if target_all:
        targets = list(inverted_index.keys())

    print(targets)
    print(bssids)
    print(network_names)
    # TODO: implement targeting the clients in `targets`


def bully_target(args):
    target_mac = args.target # MAC address string or None

    essid_data, inverted_index = discover_network()

    if target_mac not in inverted_index:
        print('target not found', file=sys.stderr)
        sys.exit(1)

    # TODO: implement bullying
    print(target_mac)


def main():
    actions = {
        'deauth': deauth_clients,
        'bully': bully_target,
        'discover': discover_network,
    }
    args = parse_args()
    actions[args.action](args)


if __name__ == '__main__':
    main()

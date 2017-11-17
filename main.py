import argparse
import re
import sys


_mac_address_pattern = re.compile('[0-9a-f]{2}(:[0-9a-f]{2}){5}')

def mac_address(addr):
    """ mac_address checks that a given string is in MAC address format """
    mac = addr.lower()
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
    
    target_group = parser.add_argument_group('target', 'specify a target machine to deauth from a network (required)')
    target_group.add_argument('-M', '--mac-addresses', action='append', nargs='+', type=mac_address, help='the MAC addresses to deauth')
    target_group.add_argument('-I', '--ip-addresses', action='append', nargs='+', type=ip_address, help='the IP address to deauth')
    target_group.add_argument('-A', '--all', action='store_true', help='target all clients on the network')

    network_group = parser.add_argument_group('network', 'specify the access points to deauth from (required)')
    network_group.add_argument('-B', '--bssids', action='append', nargs='+', type=mac_address, help='the BSSIDs of the networks to send deauth packets to')
    network_group.add_argument('-n', '--network-names', '-E', '--essids', '-S', '--ssids', action='append', nargs='+', help='the names of the networks to send deauth packets to', dest='network_names')

    subparsers = parser.add_subparsers(title="actions", description='valid actions (no action means to deauth a set of targets)', dest='action')
    bully_parser = subparsers.add_parser('bully', help='deauth a target from all networks')
    bully_target_group = bully_parser.add_mutually_exclusive_group(required=True)
    bully_target_group.add_argument('-M', '--mac-address', type=mac_address, help='the MAC address to bully')
    bully_target_group.add_argument('-I', '--ip-address', type=ip_address, help='the IP address to bully')

    args = parser.parse_args()
    if args.action is None and not args.mac_addresses and not args.ip_addresses and not args.all:
        print('Please specify a target address', file=sys.stderr)
        parser.print_usage(file=sys.stderr)
        sys.exit(1)
    return args


def deauth_clients(args):
    # targets to deauth
    mac_addresses = args.mac_addresses # list of MAC address strings or None
    ip_addresses = args.ip_addresses # list of IP address strings or None
    deauth_all = args.all # boolean

    # networks to send deauth packets too
    bssids = args.bssids # list of BSSID MAC addresses or None
    network_names = args.network_names # list of string network names or None



def bully_target(args):
    target_mac = args.mac_address # MAC address string or None
    target_ip = args.ip_address # IP address string or None


def main():
    args = parse_args()
    if args.action is None:
        deauth_clients(args)
    elif args.action == 'bully':
        bully_target(args)


if __name__ == '__main__':
    main()

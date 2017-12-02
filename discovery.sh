#!/bin/bash

discover() {
  local TIMEOUT=5s
  airmon-ng check kill >/dev/null
  ifconfig eth0 down
  airmon-ng start wlan0 >/dev/null
  gnome-terminal -e "timeout $TIMEOUT airodump-ng -c 1 -a mon0 --output-format csv -w dump"
}

discover

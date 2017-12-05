#!/bin/bash

discover() {
  local TIMEOUT=120s
#  airmon-ng check kill >/dev/null
#  ifconfig eth0 down
#  airmon-ng start wlan0 >/dev/null
  xterm +hold -e "cd /tmp && timeout $TIMEOUT airodump-ng -a wlan0mon --output-format csv -w dump"
}

discover

#!/bin/bash

discover() {
  local TIMEOUT=5s
#  airmon-ng check kill >/dev/null
#  ifconfig eth0 down
#  airmon-ng start wlan0 >/dev/null
  gnome-terminal --working-directory=/tmp -e "timeout $TIMEOUT airodump-ng -a wlan0mon --output-format csv -w dump"
}

discover

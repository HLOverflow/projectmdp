#!/bin/sh

# this is for accessing internet through Rpi when computer connect to Rpi with WIFI

if [ ! $(id -u) -eq 0 ];
then
        echo "need to run as root";
        exit 0;
fi

echo 1 | tee /proc/sys/net/ipv4/ip_forward;

iptables --flush;
iptables -t nat -A POSTROUTING -o enxb827eb6bf39f -j MASQUERADE;
#iptables -A FORWARD -i enxb827eb6bf39f -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT;
iptables -A FORWARD -i enxb827eb6bf39f -o wlan0 -j ACCEPT;
iptables -A FORWARD -i wlan0 -o enxb827eb6bf39f -j ACCEPT;
iptables --list -v;

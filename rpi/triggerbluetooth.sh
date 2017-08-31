#!/bin/bash

rfkill unblock all; 
echo -e 'power on\ndiscovery on\rnconnect 08:60:6E:A5:BA:BE\t \nquit' | bluetoothctl ;


#!/bin/sh
if [ ! $(id -u) -eq 0 ];
then
        echo "need to run as root";
        exit 0;
fi

for file in $(cat listofconfigfiles); do cp $file ./files/; done;

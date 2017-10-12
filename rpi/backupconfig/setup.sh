#!/bin/sh

if [ ! $(id -u) -eq 0 ]; 
then
	echo "need to run as root";
	exit 0;
fi

# installing softwares
echo "installing the necessary softwares...";
for software in $(cat ./listofaptget); do
	apt-get install -y $software;
	echo "installed $sofware.";
done;
echo ;

# configuration files
for i in $(ls files); do
	location=$(grep "$i\$" listofconfigfiles);
	cp $i $location;
	echo "copy $i to $location";
done;
echo ;

# make service start on reboot
for i in $(cat listofservices); do
	echo systemctl enable $i;
done;
echo ;

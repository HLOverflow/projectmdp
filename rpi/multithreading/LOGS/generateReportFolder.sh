#!/bin/sh

if [ $# -eq 0 ] || [ $# -gt 1 ];
then
	echo "[!] Usage:"
	echo "$0 <logfile>"
	exit 0
fi


filename=$1
echo "[*] processing $filename"
mkdir "$filename-OUT" &&
cat $filename | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g" > "$filename-OUT/nocolor" &&
cd "$filename-OUT" &&
grep "Sent data" nocolor | grep -o "\[[0-9].*" > "./toAll.txt" &&
echo "[*] toAll.txt generated" &&
grep "data from" nocolor | grep -o "\[[0-9].*" > "./fromAll.txt" &&
echo "[*] fromAll.txt generated" &&
grep "Sent data to arduino" nocolor | grep -o "\[[0-9].*" > "./toArduino.txt" &&
echo "[*] toArduino.txt generated" &&
grep "Sent data to bluetooth" nocolor | grep -o "\[[0-9].*" > "./toAndroid.txt" &&
echo "[*] toAndroid.txt generated"
grep "Sent data to Pc" nocolor | grep -o "\[[0-9].*" > "./toPc.txt" &&
echo "[*] toPc.txt generated" &&
grep "data from PC" nocolor | grep -o "\[[0-9].*" > "./fromPc.txt" &&
echo "[*] fromPc.txt generated" &&
grep "data from Arduino" nocolor | grep -o "\[[0-9].*" > "./fromArduino.txt" &&
echo "[*] fromArduino.txt generated" &&
grep "data from Nexus" nocolor | grep -o "\[[0-9].*" > "./fromAndroid.txt" &&
echo "[*] fromAndroid.txt generated" &&
grep "data from PC\|Sent data to arduino" nocolor | grep -o "\[[0-9].*" | grep -v "ANDROID" > "./fromPcToArduino.txt" &&
echo "[*] fromPcToArduino.txt generated" &&
grep "data from Arduino\|Sent data to Pc" nocolor | grep -o "\[[0-9].*" | grep -v "STAE" | grep -v "WP" > "./fromArduinoToPc.txt" &&
echo "[*] fromArduinoToPc.txt generated" &&
echo "End of script"
echo "Please scp the folder out to windows to convert to excel with generateExcelReport.py"
cd ..

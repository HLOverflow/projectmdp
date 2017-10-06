if [ $(id -u) -eq 0  ]; then
	for i in $( ps aux | grep "python" | awk '{print $2}'); do
		kill -9 $i;
	done;
	echo "process supposed to be killed."
	ps aux | grep "python"
else
	echo "not root"
fi

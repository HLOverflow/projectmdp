#!/usr/bin/env python

__author__ = "Tay Hui Lian"
__doc__ = "This TcpClient module is to be used for communication between raspberry pi and the desktop computer"

import traceback
import socket

class TcpClient(object):
	def __init__(self, ipaddr, port):
		'''constructor'''
		self.BUFFSIZE=1024
		self.TIMEOUT=5

		self.ipaddr=ipaddr
		self.port=port
		self.connected=False
		self.sock=socket.socket()	#TCP socket by default
		print "[*] TCP socket created"
		self.sock.settimeout(self.TIMEOUT)

	def isConnected(self):
		'''check if connected to the server'''
		return self.connected

	def setNewIp(self, ipaddr):
		'''a way to change the ip without creating another new client, ip should be a string'''
		if(type(ipaddr) == type("")):
			self.ipaddr=ipaddr
		else:
			print "Ip addr must be string"

	def setNewPort(self, port):
		'''a way to change the port number without creating another client, port should be an int'''
		if(type(port) == type(1)):
			self.port = port
		else:
			print "port must be an integer"

	def connect(self):
		'''connect to the server at ipaddr, port'''
		try:
			self.sock.connect((self.ipaddr, self.port))
			self.connected=True
			print "[*] successfully connected."
		except Exception:
			print "\n", 5*"="
			print "[!] unable to connect"
			traceback.print_exc()
			print 5*"=", "\n"
			self.connected=False

	def sendData(self, data_str):
		'''wrapper to send string data over to server'''
		if(type(data_str) != type("")):
			print "[!] data_str must be a string"
			return;
		if(self.isConnected):
			self.sock.send(data_str + "\r\n")
			print "[*] data sent:", data_str
		else:
			print "[!] Unable to send data because not connected. "

	def receiveData(self, buff):
		'''wrapper to receive data and store it inside buff, buff should be a list.'''
		if(type(buff)!=type([])):
			print "buff must be a list"
			return;

		if(self.isConnected):
			try:
				tmp = self.sock.recv(self.BUFFSIZE)
				tmp = tmp.strip()		# remove the newline \n
				print "[*] received data: ", tmp
				print "[*] saving into buff..."
				buff.append(tmp)
			except Exception:
				print 5*"="
				print "[!] unable to receive data."
				traceback.print_exc()
				print 5*"="
		else:
			print "[!] Unable to send data because not connected. "

	def disconnect(self):
		'''ensure that the connection is closed.'''
		if(self.isConnected):
			self.sock.close()
			self.connected=False
		print "[*] disconnected."

if __name__ == "__main__":
	# the following are testing purpose...
	# you can test this with simple linux netcat server
	#	nc -nlvp 8888
	# or can test with the TcpServer.py file

	client = TcpClient("127.0.0.1", 8888)
	d = []

	client.connect()

	client.sendData("abc")
	client.receiveData(d)

	client.disconnect()

	print "value of d:", d

	print "[*] end of script"

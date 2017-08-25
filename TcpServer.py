#!/usr/bin/env python

__author__ = "Tay Hui Lian"
__doc__ = "This TcpServer module is to be used for communication between raspberry pi and the desktop computer"

import traceback
import SocketServer		# easy-to-use framework for server socket programming

class MyTcpHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		'''A neccessary function for the framework to work. This function will run whenever a client connects.'''
		# receive
		self.input = self.receiveData()

		#processing (KIV)
		self.output = self.input.upper()

		#send back
		self.sendData(self.output)

		# auto disconnect on its own.

	def sendData(self, data_str):
		'''a wrapper for sending data'''
		if(type(data_str) != type("")):
                        print "[!] data_str must be a string"
                        return;
		self.request.sendall(data_str)
		print "data sent: ", data_str

	def receiveData(self):
		'''a wrapper for receiving data'''
		try:
			data = self.request.recv(1024)
			print "from: ", self.client_address[0]  # client's ip
			print "data received: ", data
			data = data.strip()		#remove \n
			return data

		except Exception:
			print 5*"="
			print "[!] unable to receive data."
			traceback.print_exc()
			print 5*"="


if __name__ == "__main__":
	host, port = "127.0.0.1", 8888
	s = SocketServer.TCPServer((host,port), MyTcpHandler)
	print "Serving server at ", host, "port", port, "..." 
	s.serve_forever()



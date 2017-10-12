#!/usr/bin/python
from Queue import Queue
from define2 import *

import socket

import traceback
from color import *
from printTime import *

class Wifi(object):
    def __init__(self, queue):
        '''Constructor will initialize and attempt to bind to port 8000'''
        self.queue = queue
        self.server = socket.socket()   #default TCP
        self.port=8000
        self.indicator = PC.NAME

        # binding to port
        try:
            self.server.bind(("", self.port))
        except socket.error as msg:
            print "[!] Bind to port %d failed.\n\tError Code: %d \n\tMessage: %s" % (self.port, msg[0], msg[1])
            traceback.print_exc()
        self.server.listen(1)
        print "[*] Wifi Initialization complete."

    def receiveUntil(self):
            buf = []
            while 1:
                char = self.client.recv(1);
                if char == '\r':
                    char = self.client.recv(1);
                    if char == '\n':
                        break
                    else:
                        print repr("didn't get \n")
                buf.append( char)
                print "appended:", repr(char)
            return ''.join(buf)

    def receiveData(self):
        '''This function is a worker function in a thread. This function will try to receive data forever from connected client.
        If connection is broken, will fall back to LISTEN state.'''

        # function with while loop should put in thread.
        while 1:        # if connection got cut off, will try to listen for new connection
            self.connect()
            while 1:    # while connection still ok, keep receiving.
                try:
                    data = self.receiveUntil();
                    if(data):
                        printWithTime( "data from PC: %s" % colorString(repr(data), PINK) )
                        self.sendData(data.upper());
                        #print "[*] received from PC and put in queue: %s" % repr(data)
                    else:
                        break           # data will be nothing when disconnected
                except socket.error as msg:
                    print "[!] Unable to receive from PC.\n\tError Code: %d\n\tMessage: %s\n" % (msg[0], msg[1])
                    #traceback.print_exc()
                    break  #accept new connections

    def sendData(self, data):
        '''This function takes care of sending data to the connected client.'''
        # for allocator to call.
        try:
            #self.connect()     # possible for connection to break when required to send data. so need check on connection and connect if needed.
            self.client.send(data + "\r\n")
            printWithTime( "[*] Sent data to Pc: %s" % repr(data) )
        except socket.error as msg:
            print "[!] Cannot send data to PC.\n\tError Code: %d\n\tMessage: %s" % (msg[0], msg[1])
            traceback.print_exc()

    def connect(self):
        '''This function will try to LISTEN for new connection.'''
        try:
             print colorString("[*] Waiting for Wifi Connection on port %s" % self.port, YELLOW)
             self.client, self.clientaddr = self.server.accept()
             print colorString("[*] Connected to PC via wifi.", GREEN)
        except:
             print "[!] Cannot accept connection to PC via wifi. "
             traceback.print_exc()

if __name__ == "__main__":
    q = Queue()
    wifi = Wifi(q)
    wifi.receiveData()
    print "program end"

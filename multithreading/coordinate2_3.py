import threading
from Queue import Queue
#from define import *

import socket
from bluetooth import *
import serial

BUF = 2048
class Wifi(object):
    def __init__(self, queue):
        self.queue = queue
        self.server = socket.socket()   #default TCP
        self.port=8000
        self.indicator = "From Pc:"

        # binding to port
        try:
            self.server.bind(("", self.port))
        except socket.error as msg:
            print "[!] Bind to port %d failed.\n\tError Code: %d \n\tMessage: %s" % (self.port, msg[0], msg[1])
        self.server.listen(1)
        print "[*] Wifi Initialization complete."

    def receiveData(self):
        # function with while loop should put in thread.
        while 1:        # if connection got cut off, will try to listen for new connection
            self.connect()
            while 1:    # while connection still ok, keep receiving.
                try:
                    data = self.client.recv(BUF)
                    if(data):
                        # possible to put processing here
                        
                        self.queue.put(self.indicator + data)       # store data into queue to be processed.
                        print "[*] received from PC and put in queue: %s" % data
                    else:
                        break			# data will be nothing when disconnected
                except socket.error as msg:
                    print "[!] Unable to receive from PC.\n\tError Code: %d\n\tMessage: %s" % (msg[0], msg[1])
                    break  #accept new connections

    def sendData(self, data):
        # for allocator to call.
        try:
            #self.connect() 	# possible for connection to break when required to send data. so need check on connection and connect if needed.
            self.client.send(data + "\r\n")
            print "[*] Send data to Pc: %s" % data
        except socket.error as msg:
            print "[!] Cannot send data to PC.\n\tError Code: %d\n\tMessage: %s" % (msg[0], msg[1])

    def connect(self):
        try:
             print "[*] Waiting for Wifi Connection on port %s" % self.port
             self.client, self.clientaddr = self.server.accept()
             print "[*] Connected to PC via wifi."
        except:
             print "[!] Cannot accept connection to PC via wifi. " 

class Bt(object):
    def __init__(self, queue):
        self.queue = queue
        self.server = BluetoothSocket(RFCOMM)
        self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        self.name = "MDP-Server"
        self.indicator = "From Bluetooth:"

        # binding to port/channel
        self.server.bind(("", PORT_ANY))
        self.server.listen(1)
        self.port = self.server.getsockname()[1]
        # advertisement
        advertise_service(self.server,
                          self.name,
                          service_id=self.uuid,
                          service_classes=[ self.uuid, SERIAL_PORT_CLASS ],
                          profiles=[ SERIAL_PORT_PROFILE ])

    def receiveData(self):
        # refer to wifi
        while 1:
            self.connect()
            while 1:
                try:
                    data = self.client.recv(BUF)
                    if(data):
                        # maybe need processing here
                        
                        self.queue.put(self.indicator + data)
                        print "[*] received from Nexus and put in queue: %s" % data
                except:
                    print "[!] Unable to receive from Nexus"
                    break
    def sendData(self, data):
        try:
            self.client.send(data + "\r\n")
            print "[*] Send data: %s" % data
        except:
            print "[!] Cannot send data to Nexus."

    def connect(self):
        try:
            print "[*] Waiting for Bluetooth Connection on port %s" % self.port
            self.client, self.clientinfo = self.server.accept()
            print "[*] Connected to Nexus via bluetooth."
        except:
            print "[!] Cannot accept connection to Nexus via bluetooth."

class Usb(object):
    def __init__(self, queue):
        self.queue = queue
        self.ports = ['/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3', '/dev/ttyACM4', '/dev/ttyACM5']
	self.baud_rate = 9600
	self.indicator = "From Arduino:"
        
    def receiveData(self):
        while 1:
            self.connect()
            while 1:
                try:
                    data = self.ser.readline()
                    # maybe can do some processing here
                    
                    self.queue.put(self.indicator + data)
                except:
                    print "[!] Unable to receive from Arduino"
                    break
    def sendData(self, data):
        try:
            self.ser.write(data + "\r\n")
            print "[*] Send data: %s" % data
        except:
            print "[!] Cannot send data to Arduino."

    def connect(self):
        for port in self.ports:
            try:
                print "[*] Attempting to connect to Arduino"
                self.ser = serial.Serial(self.port, self.baud_rate)
                print "[*] Serial link connected"
                break
            except:
                print "%s didn't work. Trying the next port" % port
        print "All serial ports listed did not work."

##class Allocator(object):
##    def __init__(self, queue, wifi, bt, usb):
##        self.wifi = wifi
##        self.bt = bt
##        self.usb = usb
##        self.queue = queue
##
##    def allocate(self):
##        while 1:
##            data=self.queue.get()
##            if self.wifi.indicator in data:
##                self.bt.sendData(data)
##                self.usb.sendData(data)
##            elif self.bt.indicator in data:
##                self.usb.sendData(data)
##                self.wifi.sendData(data)
##            elif self.usb.indicator in data:
##                self.wifi.sendData(data)
##                self.bt.sendData(data)
##            else:
##                pass

# mini test for just wifi, bluetooth and usb
def allocate(queue, wifi, bt, usb):
    while 1:
        data = queue.get()
        if wifi.indicator in data:
            # any processing before send can put here
            
            bt.sendData(data)
            usb.sendData(data)
        elif bt.indicator in data:
            # any processing before send can put here
            
            wifi.sendData(data)
            usb.sendData(data)
        elif usb.indicator in data:
            # any processing before send can put here
            
            wifi.sendData(data)
            bt.sendData(data)
        else:
            print "data not sent to anyone: %s" % data
            pass

if __name__ == "__main__":
    q = Queue()
    wifi = Wifi(q)
    bt = Bt(q)
    usb = Usb(q)
    
    wifi_receive = threading.Thread(target=wifi.receiveData);
    bt_receive = threading.Thread(target=bt.receiveData);
    usb_receive = threading.Thread(target=usb.receiveData);
    
    allocator = threading.Thread(target=allocate, args=(q, wifi, bt, usb));

    wifi_receive.start()
    bt_receive.start()
    usb_receive.start()
    allocator.start()
    

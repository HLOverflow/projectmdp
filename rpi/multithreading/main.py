#!/usr/bin/python
import time
import threading
from Queue import Queue
from define2 import *

import socket
from bluetooth import *
import serial

import traceback
from color import *
from printTime import *

# pi@MDPGrp25:~/shortcut $ python
# Python 2.7.13 (default, Jan 19 2017, 14:48:08)
# [GCC 6.3.0 20170124] on linux2
# Type "help", "copyright", "credits" or "license" for more information.
# >>> import testAll3
# >>> help(testAll3)

__author__ = "Hui Lian"
__doc__ = '''This is to be loaded inside Raspberry Pi. 

Abort by Ctrl-C. Should be able to terminate gracefully.

This program should be ran with the following commands for best results:

$ script LOGS/<filename>
$ sudo python main.py
# exit

------------------------
This will set up a total of 5 threads: 
3 threads for each receiving + 1 allocate thread for general sending + 1 special thread for arduino sending.

There are 2 queues in this program:
1) queue
- all receiving threads will put data into queue
- allocate will get data from queue and send the data to their recipient. 
- if recipient is arduino, send data into another queue_usb.
2) queue_usb
- arduino sending thread will take from this queue_usb.

Data storage in the queues are using data structure: Letter from define2.py
-------------------------
Good features:
- text colors in linux terminal
- timestamp are printed for important sections
- when connections are broken for Wifi and Bluetooth, the port becomes LISTENING again.
- Translation done for arduino integers command for Android and PC.
--------------------------
Possible issue faced:
- If wifi cannot bind to port 8000, wait for a few minute until netstat for port 8000 stops FIN_WAIT2.
$ netstat -antp

'''

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

    def generateLetter(self, data):
        '''generate a Letter object with correct recipient. Function will check for recipient in the header, then will remove the header from the data.'''
        letter = Letter()
        letter.From = self.indicator

        if RPI.NAME in data:
            letter.To = RPI.NAME
            letter.Message = data[len(RPI.NAME)+1:]
        elif ANDROID.NAME in data:
            letter.To = ANDROID.NAME
            letter.Message = data[len(ANDROID.NAME)+1:]
        elif ARDUINO.NAME in data:
            letter.To = ARDUINO.NAME
            letter.Message = data[len(ARDUINO.NAME)+1:]
        else:
            letter.To = ARDUINO.NAME
            letter.Message = data[len(ARDUINO.NAME)+1:]
        return letter

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
            #print "appended:", repr(char)
        return ''.join(buf)


    def receiveData(self):
        '''This function is a worker function in a thread. This function will try to receive data forever from connected client. 
        If connection is broken, will fall back to LISTEN state.'''

        # function with while loop should put in thread.
        while not self.End:        # if connection got cut off, will try to listen for new connection
            self.connect()
            while 1:    # while connection still ok, keep receiving.
                try:
                    data = self.receiveUntil()
                    if(data):
                        printWithTime( "data from PC: %s" % colorString(repr(data), PINK) )
                        letter = self.generateLetter(data)
                        letter.printcontent()
                        self.queue.put(letter)       # store data into queue to be processed.
                        #print "[*] received from PC and put in queue: %s" % repr(data)
                    else:
                        break           # data will be nothing when disconnected
                except socket.error as msg:
                    print "[!] Unable to receive from PC.\n\tError Code: %d\n\tMessage: %s\n" % (msg[0], msg[1])
                    break  #accept new connections
        # End gracefully
        self.endGracefully()

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

    def endGracefully(self):
        self.server.shutdown(socket.SHUT_RDWR)      #clear away all data with client first
        self.server.close()
        print "wifi closed."
        

class Bt(object):
    def __init__(self, queue):
        '''Constructor will initialize and advertise the bluetooth service as "MDP-Server". '''
        self.queue = queue
        self.server = BluetoothSocket(RFCOMM)
        self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        self.name = "MDP-Server"
        self.indicator = ANDROID.NAME
        self.End = False

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

    def generateLetter(self, data):
        '''generate a Letter object with correct recipient. Function will check for recipient in the header, then will remove the header from the data.'''
        letter = Letter()
        letter.From = self.indicator

        if PC.NAME in data:
            letter.To = PC.NAME
            letter.Message = data[len(PC.NAME)+1:]
        elif RPI.NAME in data:
            letter.To = RPI.NAME
            letter.Message = data[len(RPI.NAME)+1:]
        else:
            letter.To = ARDUINO.NAME
            letter.Message = data[len(ARDUINO.NAME)+1:]
        return letter
            
    def receiveData(self):
        '''This function is a worker function in a thread. This function will try to receive data forever from connected client. 
        If connection is broken, will fall back to LISTEN state.'''

        while not self.End:
            self.connect()
            while 1:
                try:
                    data = self.client.recv(BUF)
                    if(data):
                        # maybe need processing here
                        printWithTime( "data from Nexus: %s" % colorString(repr(data), PINK))
                        letter = self.generateLetter(data)
                        letter.printcontent()
                        self.queue.put(letter)
                        #print "[*] received from Nexus and put in queue: %s" % repr(data)
                except:
                    print "[!] Unable to receive from Nexus"
                    #traceback.print_exc()
                    break
        # end gracefully
        self.endGracefully()
        
    def sendData(self, data):
        '''This function takes care of sending data to the connected client.'''
        try:
            self.client.send(data + "\r\n")
            printWithTime( "Sent data to bluetooth: %s" % repr(data) )
        except:
            print "[!] Cannot send data to Nexus."
            traceback.print_exc()

    def connect(self):
        '''This function will try to LISTEN for new connection.'''
        try:
            print colorString("[*] Waiting for Bluetooth Connection on port %s" % self.port, YELLOW)
            self.client, self.clientinfo = self.server.accept()
            print colorString("[*] Connected to Nexus via bluetooth.", GREEN)
        except:
            print "[!] Cannot accept connection to Nexus via bluetooth."
            traceback.print_exc()

    def endGracefully(self):
        self.server.close()
        print "Bluetooth closed."
    

class Usb(object):
    def __init__(self, queue):
        self.queue = queue
        self.ports = ['/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3', '/dev/ttyACM4', '/dev/ttyACM5']
        self.baud_rate = 2000000
        self.indicator = ARDUINO.NAME
        self.readytosend = False
        self.isconnected = False

    def generateLetter(self, data):
        '''generate a Letter object to PC. There is no header truncation here because the only recipient is PC.'''
        letter = Letter()

        letter.Message = data
        letter.From = self.indicator

        #no other route
        letter.To = PC.NAME
        return letter
        
    def receiveData(self):  # sensor data from arduino
        '''This function is a worker function in a thread. This function will try to receive data forever from Arduino. 
        If connection is broken, will try to reconnect to the USB for a max of 5 times before giving up.
        This receive function is slightly more special than the rest, with the additional check for READY signal from arduino as a trigger to the sending thread.
        ''' 
        count = 0
        while count < 5:
            count+=1
            self.isconnected = self.connect()
            if self.isconnected:
                while 1:
                    try:
                        data = self.ser.readline()   # arduino will send us string. 
                        if data:
                            printWithTime( "data from Arduino: %s" % colorString(repr(data), PINK) )
                            if ARDUINO.ARDUINO_READY in data:
                                self.readytosend = True
                                printWithTime( colorString("\tArduino sent rpi READY SIGNAL.", GREEN) )
                            else:
                                if ARDUINO.SENSOR_DATA_RESPONSE in data:
                                    # send
                                    letter = self.generateLetter(data) #perhaps no need letter for arduino. can possibly connect to Rpi directly.
                                    letter.printcontent()
                                    self.queue.put(letter)
                                    #print "[*] received from arduino and put in queue: %s" % data
                    except:
                        print "[!] Unable to receive from Arduino"
                        traceback.print_exc()
                        break
            else:
                print "not connected to arduino."
        print "[!] Check your USB port! "
                
    def sendData(self, cmd):   # commands to arduino
        '''This function takes care of sending data to arduino.'''
        try:
            self.ser.write(bytes(cmd))
            printWithTime( "Sent data to arduino: %s" % repr(cmd))
        except:
            print "[!] Cannot send data to Arduino."
            traceback.print_exc()
        finally:
            self.readytosend = False                #after every send. must set this back to false.

    def connect(self):
        '''This function attempts to brute force possible serial ports for the arduino because the OS randomize the path of the port after each physical connections.'''
        for port in self.ports:
            try:
                print "[*] Attempting to connect to Arduino"
                self.ser = serial.Serial(port, self.baud_rate, timeout=1)
                print "[*] Serial link connected"
                return True
            except:
                print "%s didn't work. Trying the next port" % port
                #traceback.print_exc()
        print "[!] All serial ports listed did not work."
        return False

    def wait(self):
        '''This is a function to BLOCK the sending thread until READY signal is received.'''
        while(not usb.readytosend):
            pass
        print colorString("exit usb wait.", GREEN)
        return None

def arduinoSending(queue_usb, usb):
    while 1:
    	if queue_usb.empty():
    		continue
        cmd = queue_usb.get()
        #print "[arduinoSending] got cmd from queue_usb:", repr(cmd)
        #print "[arduinoSending] content of queue_usb: ", queue_usb.queue
        print colorString("[arduinoSending] waiting FOR READY SIGNAL...", YELLOW)
        usb.wait()                      # wait for READY signal from arduino.
        usb.sendData(cmd)


def allocate(queue, queue_usb, wifi, bt, usb):
    '''Constantly get letter from queue and sending them to correct destination.'''
    while 1:
    	if queue.empty():
    		continue
        letter = queue.get()
        #print "[*] Sending letter from [%s] to [%s]." % (letter.From, letter.To)
        data = letter.Message
        if wifi.indicator in letter.To:
            wifi.sendData(data)
        elif bt.indicator in letter.To:
            bt.sendData(data)
        elif usb.indicator in letter.To:
            # must do translation before sending!!!
            # have to block the send until can verify arduino is ready
            if letter.From == ANDROID.NAME:
                cmd = AndroidtoArduinoTranslate(data)
                queue_usb.put(cmd);         # delegate the work to the another thread, prevents blocking in this thread.
            elif letter.From == PC.NAME:
                cmd = PCtoArduinoTranslate(data)
                queue_usb.put(cmd)          # delegate the work to the another thread, prevents blocking in this thread.
            else:
                pass
        else:
            print "[!] data not sent to anyone: %s" % data
            pass

def AndroidtoArduinoTranslate(data):
    output=''
    if ANDROID.MOVE_FORWARD in data:
        output=ARDUINO.MOVE_FORWARD
    elif ANDROID.ROTATE_LEFT in data:
        output=ARDUINO.ROTATE_LEFT
    elif ANDROID.ROTATE_RIGHT in data:
        output=ARDUINO.ROTATE_RIGHT
    elif ANDROID.ROTATE_RIGHT in data:
        output=ARDUINO.ROTATE_RIGHT
    else:
        print colorString("[!] didn't translate sucessfully: ", RED), repr(data)
    #print "[*] translation:", repr(data), "-->" , repr(output)
    return output

def PCtoArduinoTranslate(data):
    output=''
    if PC.MOVE_FORWARD in data:
        output=ARDUINO.MOVE_FORWARD
    elif PC.ROTATE_LEFT in data:
        output=ARDUINO.ROTATE_LEFT
    elif PC.ROTATE_RIGHT in data:
        output=ARDUINO.ROTATE_RIGHT
    elif PC.MOVE_FORWARD_XCM.search(data):
        cm=PC.MOVE_FORWARD_XCM.findall(data)[0]
        output='a'.join([ARDUINO.MOVE_FORWARD_XCM,cm])
    elif PC.GET_SENSOR_DATA in data:
        output=ARDUINO.GET_SENSOR_DATA
    else:
        print colorString("[!] didn't translate sucessfully: ", RED), repr(data)
    #print "[*] translation:", repr(data), "-->" , repr(output)
    return output

if __name__ == "__main__":
    q = Queue()
    q_usb = Queue()
    wifi = Wifi(q)
    bt = Bt(q)
    usb = Usb(q)

    # Receiving
    wifi_receive = threading.Thread(target=wifi.receiveData)
    bt_receive = threading.Thread(target=bt.receiveData)
    usb_receive = threading.Thread(target=usb.receiveData)

    # Sending
    arduino_send = threading.Thread(target=arduinoSending, args=(q_usb, usb))

    # moving this thread to main.
    #allocator = threading.Thread(target=allocate, args=(q, q_usb, wifi, bt, usb))

    # not sure if should set these threads as daemon...
    # wifi_receive.daemon = True
    # bt_receive.daemon = True
    # usb_receive.daemon = True
    arduino_send.daemon = True          # set as daemon because it is not a class. can't implement Signals.

    wifi_receive.start()
    bt_receive.start()
    usb_receive.start()
    arduino_send.start()
    
    #allocator.start()
    try:
        allocate(q, q_usb, wifi, bt, usb)
    except KeyboardInterrupt:
        print "received abort signal."
        wifi.End = True
        bt.End = True
    except:
        traceback.print_exc()

    print "program end"
    

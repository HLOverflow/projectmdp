#!/usr/bin/python

import threading
from Queue import Queue
from define2 import *

import socket
from bluetooth import *
import serial

import traceback
from color import *
from printTime import *

class Wifi(object):
    def __init__(self, queue):
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

    def receiveData(self):
        # function with while loop should put in thread.
        while 1:        # if connection got cut off, will try to listen for new connection
            self.connect()
            while 1:    # while connection still ok, keep receiving.
                try:
                    data = self.client.recv(BUF)
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
                    #traceback.print_exc()
                    break  #accept new connections

    def sendData(self, data):
        # for allocator to call.
        try:
            #self.connect()     # possible for connection to break when required to send data. so need check on connection and connect if needed.
            self.client.send(data + "\r\n")
            printWithTime( "[*] Sent data to Pc: %s" % repr(data) )
        except socket.error as msg:
            print "[!] Cannot send data to PC.\n\tError Code: %d\n\tMessage: %s" % (msg[0], msg[1])
            traceback.print_exc()

    def connect(self):
        try:
             print colorString("[*] Waiting for Wifi Connection on port %s" % self.port, YELLOW)
             self.client, self.clientaddr = self.server.accept()
             print colorString("[*] Connected to PC via wifi.", GREEN)
        except:
             print "[!] Cannot accept connection to PC via wifi. "
             traceback.print_exc()

class Bt(object):
    def __init__(self, queue):
        self.queue = queue
        self.server = BluetoothSocket(RFCOMM)
        self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        self.name = "MDP-Server"
        self.indicator = ANDROID.NAME

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
        # refer to wifi
        while 1:
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
    def sendData(self, data):
        try:
            self.client.send(data + "\r\n")
            printWithTime( "Sent data to bluetooth: %s" % repr(data) )
        except:
            print "[!] Cannot send data to Nexus."
            traceback.print_exc()

    def connect(self):
        try:
            print colorString("[*] Waiting for Bluetooth Connection on port %s" % self.port, YELLOW)
            self.client, self.clientinfo = self.server.accept()
            print colorString("[*] Connected to Nexus via bluetooth.", GREEN)
        except:
            print "[!] Cannot accept connection to Nexus via bluetooth."
            traceback.print_exc()

class Usb(object):
    def __init__(self, queue):
        self.queue = queue
        self.ports = ['/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3', '/dev/ttyACM4', '/dev/ttyACM5']
        self.baud_rate = 2000000
        self.indicator = ARDUINO.NAME
        self.readytosend = False
        self.isconnected = False
        self.timing = 0.0

    def generateLetter(self, data):
        letter = Letter()

        letter.Message = data
        letter.From = self.indicator

        #no other route
        letter.To = PC.NAME
        return letter
        
    def receiveData(self):  # sensor data from arduino
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
        try:
            self.ser.write(bytes(cmd))
            printWithTime( "Sent data to arduino: %s" % repr(cmd))
        except:
            print "[!] Cannot send data to Arduino."
            traceback.print_exc()
        finally:
            self.readytosend = False                #after every send. must set this back to false.

    def connect(self):
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
        while(not usb.readytosend):
            pass
        print colorString("exit usb wait.", GREEN)
        return None

def arduinoSending(queue_usb, usb):
    while 1:
    	if queue_usb.empty():
    		continue
        cmd = queue_usb.get()
        print "[arduinoSending] got cmd from queue_usb:", repr(cmd)
        print "[arduinoSending] content of queue_usb: ", queue_usb.queue
        print colorString("[arduinoSending] waiting FOR READY SIGNAL...", YELLOW)
        usb.wait()                      # wait for READY signal from arduino.
        usb.sendData(cmd)


def allocate(queue, queue_usb, wifi, bt, usb):
    '''Constantly get letter from queue and sending them to correct destination.'''
    while 1:
    	if queue.empty():
    		continue
        letter = queue.get()
        print "[*] Sending letter from [%s] to [%s]." % (letter.From, letter.To)
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
    print "[*] translation:", repr(data), "-->" , repr(output)
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
    print "[*] translation:", repr(data), "-->" , repr(output)
    return output

if __name__ == "__main__":
    q = Queue()
    q_usb = Queue()
    wifi = Wifi(q)
    bt = Bt(q)
    usb = Usb(q)

    #wifi_receive = threading.Thread(target=wifi.receiveData)
    bt_receive = threading.Thread(target=bt.receiveData)
    usb_receive = threading.Thread(target=usb.receiveData)

    arduino_send = threading.Thread(target=arduinoSending, args=(q_usb, usb))    
    allocator = threading.Thread(target=allocate, args=(q, q_usb, wifi, bt, usb))

    #wifi_receive.start()
    bt_receive.start()
    usb_receive.start()
    arduino_send.start()
    allocator.start()

    # not sure if these will help at the end because the thread tasks are always running in a while loop...
    #wifi_receive.join()
    bt_receive.join()
    usb_receive.join()
    arduino_send.join()
    allocator.join()
    print "program end"
    

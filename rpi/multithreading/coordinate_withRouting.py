import threading
from Queue import Queue
from define2 import *

import socket
from bluetooth import *
import serial

# what has changed?
# - introduced Letter in define2.py
# - For each component, upon receiving data will generate a letter to address to correct destination.
# - queue no longer holds pure data string but letters(easier for sending).
# - introduced RaspberryPi class for storing map and maybe process arduino's sensor data(not sure how though)?
# - RaspberryPi's replying the "Request Arena" with 2 letters separately(for MDF1 and MDF2), perhaps can combine into 1 single letter?
# - code cannot be tested until actual integration. Plz help review the code to reduce errors. Thanks!

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
        self.server.listen(1)
        print "[*] Wifi Initialization complete."

    def generateLetter(self, data):
        letter = Letter()
        letter.Message = data
        letter.From = self.indicator
        if PC.REQ_ARENA in data:
            letter.To = RPI.NAME
        else:
            letter.To = ARDUINO.NAME
        return letter

    def receiveData(self):
        # function with while loop should put in thread.
        while 1:        # if connection got cut off, will try to listen for new connection
            self.connect()
            while 1:    # while connection still ok, keep receiving.
                try:
                    data = self.client.recv(BUF)
                    if(data):
                        # possible to put processing here  
                        letter = self.generateLetter(data)
                        self.queue.put(letter)       # store data into queue to be processed.
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
        letter.Message = data
        letter.From = self.indicator
        # deciding To field.
        if ANDROID.REQ_ARENA in data:
            letter.To = RPI.NAME
        elif (ANDROID.MOVE_FORWARD in data)    \
             or (ANDROID.ROTATE_LEFT in data)  \
             or (ANDROID.MOVE_FORWARD in data) \
             or (ANDROID.ROTATE_RIGHT in data) \
             or (ANDROID.ROTATE_180 in data):
            letter.To = ARDUINO.NAME
        else:
            # default route to PC
            letter.To = PC.NAME
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
                        letter = self.generateLetter(data)
                        
                        self.queue.put(letter)
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
        self.ports = ['/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3', '/dev/ttyACM4', '/dev/ttyACM5', '/dev/ttyAMA0', '/dev/ttyAMA1','/dev/ttyAMA2', '/dev/ttyAMA3', '/dev/ttyAMA4', '/dev/ttyAMA5' ]
        self.baud_rate = 2000000
        self.indicator = ARDUINO.NAME
        self.readytosend = false

    def generateLetter(self, data):
        letter = Letter()
        letter.Message = data
        letter.From = self.indicator

        #no other route - do we even need a letter? Rpi can directly process
        letter.To = RPI.NAME
        return letter
        
    def receiveData(self):  # sensor data from arduino
        while 1:
            self.connect()
            while 1:
                try:
                    data = self.ser.readline()   # arduino will send us string. 
                    if ARDUINO.ARDUINO_READY in data:
                        self.readytosend = true
                    else:
                        letter = self.generateLetter(data) #perhaps no need letter for arduino. can possibly connect to Rpi directly.
                        self.queue.put(letter)
                except:
                    print "[!] Unable to receive from Arduino"
                    break
    def sendData(self, cmd):   # commands to arduino ( rpi must send int bytes)
        try:
            self.ser.write(bytes(cmd))
            print "[*] Send data: %x" % cmd
            self.readytosend = false
        except:
            print "[!] Cannot send data to Arduino."

    def connect(self):
        for port in self.ports:
            try:
                print "[*] Attempting to connect to Arduino"
                self.ser = serial.Serial(port, self.baud_rate, timeout=1)
                print "[*] Serial link connected"
                break
            except:
                print "%s didn't work. Trying the next port" % port
        print "All serial ports listed did not work."

class RaspberryPi(object):
    '''Rpi have to keep a memory of the map (explored vs unexplored and obstacles vs free)'''
    def __init__(self, queue):
        self.queue = queue
        self.mapstr = ""            
        self.indicator = RPI.NAME

    def updateMap(self, data):
        '''update our MDF1 and MDF2'''
        # not sure what to do here yet.
        self.mapstr = PC.SEND_ARENA.findall(data)[0]
        

    def requestArena(self, replyto):
        '''Replying the arena request with MDF1 and MDF2. '''
        # first letter for MDF1
        letter1 = Letter()
        letter1.From = self.indicator
        letter1.To = replyto
        letter1.Message = self.mapstr
        self.queue.put(letter1)

    def processRequest(self, data):
        '''Given the letter message, determine if message is for updating map or just a requesting for the map'''
        if ANDROID.REQ_ARENA in data:
            self.requestArena(ANDROID.NAME)
#        elif PC.REQ_ARENA in data:
#            self.requestArena(PC.NAME)
        elif ARDUINO.ARDUINO_READY in data:
            self.usb.readytosend = true
        else:
            # should be arduino's sensor data to be processed by rpi.
            self.updateMap(data)

def allocate(queue, wifi, bt, usb, rpi):
    '''Constantly get letter from queue and sending them to correct destination.'''
    while 1:
        letter = queue.get()
        print "Sending letter from [%s] to [%s]." % (letter.From, letter.To)
        data = letter.Message
        if wifi.indictor in letter.To:
            wifi.sendData(data)
        elif bt.indictor in letter.To:
            bt.sendData(data)
        elif usb.indicator in letter.To:
            # have to block the send until can verify arduino is ready
            while !usb.readytosend:
                pass
            # must do translation before sending!!!
            if letter.From == ANDROID.NAME:
                cmdarray = AndroidtoArduinoTranslate(data)
                for cmd in cmdarray:
                    usb.sendData(cmd)
            elif letter.From == PC.NAME:
                cmdarray = PCtoArduinoTranslate(data)
                for cmd in cmdarray:
                    usb.sendData(cmd)
            else:
                pass
        elif RPI.NAME in letter.To:
            # rpi should process this data for local map.
            # rpi processing below (RPI might need its own thread?)
            rpi.processRequest(data)
        else:
            print "data not sent to anyone: %s" % data
            pass

def AndroidtoArduinoTranslate(data):
    output=[]
    if ANDROID.MOVE_FORWARD in data:
        output=[ARDUINO.MOVE_FORWARD]
    elif ANDROID.ROTATE_LEFT in data:
        output=[ARDUINO.ROTATE_LEFT]
    elif ANDROID.ROTATE_RIGHT in data:
        output=[ARDUINO.ROTATE_RIGHT]
    elif ANDROID.ROTATE_RIGHT in data:
        output=[ARDUINO.ROTATE_RIGHT]
    else:
        pass
    return output

def PCtoArduinoTranslate(data):
    output=[]
    if PC.MOVE_FORWARD in data:
        output=[ARDUINO.MOVE_FORWARD]
    elif PC.ROTATE_LEFT in data:
        output=[ARDUINO.ROTATE_LEFT]
    elif PC.ROTATE_RIGHT in data:
        output=[ARDUINO.ROTATE_RIGHT]
    elif PC.ROTATE_RIGHT in data:
        output=[ARDUINO.ROTATE_RIGHT]
    elif PC.MOVE_FORWARD_XCM.search(data):
        cm=int(PC.MOVE_FORWARD_XCM.findall(data)[0])
        output=[ARDUINO.MOVE_FORWARD_XCM,cm]
    else:
        pass
    return output

if __name__ == "__main__":
    q = Queue()
    wifi = Wifi(q)
    bt = Bt(q)
    usb = Usb(q)
    rpi = RaspberryPi(q)
    
    wifi_receive = threading.Thread(target=wifi.receiveData);
    bt_receive = threading.Thread(target=bt.receiveData);
    usb_receive = threading.Thread(target=usb.receiveData);
    
    allocator = threading.Thread(target=allocate, args=(q, wifi, bt, usb, rpi));

    wifi_receive.start()
    bt_receive.start()
    usb_receive.start()
    allocator.start()

    # not sure if these will help at the end because the thread tasks are always running in a while loop...
    wifi_receive.join()
    bt_receive.join()
    usb_receive.join()
    allocator.join()
    print "program end"
    

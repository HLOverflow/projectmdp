import serial
import threading
from Queue import Queue
from define2 import *
import traceback
from color import *
from printTime import *
import time

class Usb(object):
    def __init__(self, queue):
        self.queue = queue
        self.ports = ['/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3', '/dev/ttyACM4', '/dev/ttyACM5']
        self.baud_rate = 115200
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
                self.ser = serial.Serial(port, self.baud_rate, timeout=0.8)
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
        # should i do a delay here???
        # time.sleep(0.1)
        usb.sendData(cmd)

def allocate(queue, queue_usb, usb):
    '''Constantly get letter from queue and sending them to correct destination.'''
    instructions = ['226', '226', '226', '226', '226', '226', '228', '226', '226', '226', '226', '226', '226', '228', '226', '226', '226', '226', '226', '226', '229', '226', '226', '226', '226', '226', '226', '229', '226', '226', '226', '226', '226', '229', '226', '226', '226', '228', '226', '226', '226', '226', '226', '226', '228', '226', '226', '226', '229', '226', '226'
    ]
    for i in instructions:
    	queue_usb.put(i);
    print "putted all commands in the queue."

    while not queue_usb.empty():
    	continue
    print "no more commands"

if __name__ == "__main__":
	q = Queue()
    q_usb = Queue()
    usb = Usb(q)

    usb_receive = threading.Thread(target=usb.receiveData)
    arduino_send = threading.Thread(target=arduinoSending, args=(q_usb, usb))

    usb_receive.daemon = True
    arduino_send.daemon = True

    usb_receive.start()
    arduino_send.start()

    try:
        allocate(q, q_usb, usb)
    except:
        traceback.print_exc()
        exit(0)
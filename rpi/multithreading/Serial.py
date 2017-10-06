import serial
import time

ARDUINO_READY = 0xE0
RPI_READY = 0xE1
MOVE_FORWARD = 0xE2
MOVE_FORWARD_XCM = 0xE3
ROTATE_LEFT = 0xE4
ROTATE_RIGHT = 0xE5
GET_SENSOR_DATA = 0xE6
CALIBRATE = 0xE7
MOVE_REVERSE = 0xE8
MOVE_REVERSE_XCM = 0xE9

ROTATE_XDEG = 0xEA
SEQUENTIAL_COMMANDS = 0xED
MOVE_SQUARE = 0xEE
CMD_ERROR = 0xEF

baud=2000000
# brute forcing the ports
ports = ['/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3', '/dev/ttyACM4', '/dev/ttyACM5']
flag=0
for port in ports:
    try:
        print "[*] Attempting to connect to Arduino"
        ard = serial.Serial(port, baud, timeout=1)
        print "[*] Serial link connected"
        flag=0
        break
    except:
        print "%s didn't work. Trying the next port" % port
        flag=1
if flag:
    print "All serial ports listed did not work."
    exit(0)

time.sleep(2)

while(True):
    #wait for arudino to be ready
    status = ard.read(16)
#    print "data type of status: ", type(status), status
    if(status):
        try:
            if(int(status) == ARDUINO_READY):
                print "Arduino Ready"
        except:
            print "received: %s" % status
    else:
        continue;
        
    # ask for user input
    print("Enter input")
    cmd = raw_input()
    print "entered cmd:", cmd
    if(str(MOVE_FORWARD) in cmd):
        print "send move forward"
    elif(str(ROTATE_LEFT) in cmd):
        print "Send rotate left"
    elif(str(ROTATE_RIGHT) in cmd):
        print "Send rotate right"
    elif(str(GET_SENSOR_DATA) in cmd):
        print "send get sensor data"
    elif(str(MOVE_FORWARD_XCM) in cmd):
    	print "send move forward X cm"
    elif(str(CALIBRATE) in cmd):
        print "send calibrate"
    elif(str(255) in cmd):
        print "experimental command"
    
    else:
        print "Invalid Command"
        continue
        
    ard.write(bytes(cmd))
    #;
    
    #wait for echo back
    #status = ard.read(4);
    #if(int(status) == MOVE_FORWARD):
        #print("Arudino moving forward")
    #else:
       # print(status.encode("hex"))
        #print("No msg")
        
        
        

import threading
from Queue import Queue
from define2 import *

import socket
from bluetooth import *
import serial

import traceback

def PCtoArduinoTranslate(data):
    output=[]
    if PC.MOVE_FORWARD in data:
        output=[ARDUINO.MOVE_FORWARD]
    elif PC.ROTATE_LEFT in data:
        output=[ARDUINO.ROTATE_LEFT]
    elif PC.ROTATE_RIGHT in data:
        output=[ARDUINO.ROTATE_RIGHT]
    elif PC.MOVE_FORWARD_XCM.search(data):
        cm=PC.MOVE_FORWARD_XCM.findall(data)[0]
        output=[ARDUINO.MOVE_FORWARD_XCM,cm]
    elif PC.GET_SENSOR_DATA in data:
        output=[ARDUINO.GET_SENSOR_DATA]
    else:
        print "[!] didn't translate sucessfully: ", repr(data)
        pass
    print "[*] translation:", repr(data), "-->" ,output
    return output

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
    print "[*] translation:", repr(data), "-->" , output
    return output


if __name__ == "__main__":
    command = "RS\r\n"
    result = PCtoArduinoTranslate(command)
    print "command: %s" % repr(command)
    print "result: %s" % repr(result)

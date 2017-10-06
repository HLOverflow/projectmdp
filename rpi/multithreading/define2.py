import re

BUF=2048

class Letter:
    def __init__(self):
        self.From = None
        self.To = None
        self.Message = None

    def printcontent(self):
        print "FROM: %s TO: %s MESSAGE: %s" % (self.From, self.To, repr(self.Message))

class ANDROID:
    NAME = "ANDROID"
    REQ_ARENA = "RA"
    MOVE_FORWARD = "FC"
    ROTATE_LEFT = "LC"
    ROTATE_RIGHT = "RC"
    ROTATE_180 = "RB" #notneeded
    SET_STARTPOINT = "SP:"
    SET_WAYPOINT = "WP:"
    START_EXPLORE = "STAE"
    START_SHORTESTPATH = "SSP"

class PC:
    NAME = "ALGO"
    SEND_ARENA = re.compile("MAP (.+?)")
    MOVE_FORWARD = "INS:F"
    MOVE_FORWARD_XCM = re.compile("INS:(\d+)")
    ROTATE_LEFT = "INS:L"
    ROTATE_RIGHT = "INS:R"
    REVERSE = "INS:B"
    CALIBRATE = "INS:C" #kiv
    ROTATE_180 = "\xA4" #notneeded
    GET_SENSOR_DATA = "RS"

class ARDUINO:
    NAME = "ARDUINO"
    ARDUINO_READY = str(0xe0)
    RPI_READY = str(0xe1)            #need anot? actually no need.
    MOVE_FORWARD = str(0xe2)
    MOVE_FORWARD_XCM = str(0xe3)
    ROTATE_LEFT = str(0xe4)
    ROTATE_RIGHT = str(0xe5)
    REVERSE = "?"
    GET_SENSOR_DATA = str(0xe6)
    SENSOR_DATA_RESPONSE = str(0xea)

class RPI:
    NAME = "RPI"

import re

BUF=2048

class Letter:
    def __init__(self):
        self.From = None
        self.To = None
        self.Message = None

    def printcontent(self):
        print "FROM: %s TO: %s MESSAGE: %s" % (self.From, self.To, self.Message)

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
    SEND_ARENA = re.compile("MAP (.+?)\n")
    MOVE_FORWARD = "INS\nF\n"
    MOVE_FORWARD_XCM = re.compile("INS\n(\d+?)\n")
    ROTATE_LEFT = "INS\nL\n"
    ROTATE_RIGHT = "INS\nR\n"
    REVERSE = "INS\nB\n"
    CALIBRATE = "INS\nC\n" #kiv
    ROTATE_180 = "\xA4" #notneeded


class ARDUINO:
    NAME = "ARDUINO"
    ARDUINO_READY = str(0xe0)
    RPI_READY = str(0xE1)            #need anot? actually no need.
    MOVE_FORWARD = str(0xE2)
    MOVE_FORWARD_XCM = str(0xE3)
    ROTATE_LEFT = str(0xE4)
    ROTATE_RIGHT = str(0xE5)
    REVERSE = "?"
    GET_SENSOR_DATA = str(0xE6)
    SENSOR_DATA_RESPONSE = str(0xef)

class RPI:
    NAME = "RPI"

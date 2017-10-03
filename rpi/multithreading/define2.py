import re

class Letter:
    def __init__(self):
        self.From = None
        self.To = None
        self.Message = None

class ANDROID:
    NAME = "Android"
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
    NAME = "PC"
    SEND_ARENA = re.compile("MAP (.+?)\n")
    MOVE_FORWARD = "INS\nF\n"
    MOVE_FORWARD_XCM = re.compile("INS\n(\d+?)\n")
    ROTATE_LEFT = "INS\nL\n"
    ROTATE_RIGHT = "INS\nR\n"
    REVERSE = "INS\nB\n"
    CALIBRATE = "INS\nC\n" #kiv
    ROTATE_180 = "\xA4" #notneeded


class ARDUINO:
    NAME = "Arduino"
    ARDUINO_READY = "225"
    RPI_READY = 0xE1            #need anot? actually no need.
    MOVE_FORWARD = 0xE2
    MOVE_FORWARD_XCM = 0xE3
    ROTATE_LEFT = 0xE4
    ROTATE_RIGHT = 0xE5
    REVERSE = "?"
    GET_SENSOR_DATA = 0xE6

class RPI:
    NAME = "Rpi"

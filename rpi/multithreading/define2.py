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
    ROTATE_180 = "RB"
    SET_STARTPOINT = "SP:"
    SET_WAYPOINT = "WP:"
    START_EXPLORE = "STAE"
    START_SHORTESTPATH = "SSP"

class PC:
    NAME = "PC"
    REQ_ARENA = "\xA0"
    MOVE_FORWARD = "\xA1"
    ROTATE_LEFT = "\xA2"
    ROTATE_RIGHT = "\xA3"
    ROTATE_180 = "\xA4"

class ARDUINO:
    NAME = "Arduino"

class RPI:
    NAME = "Rpi"

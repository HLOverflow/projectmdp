from define2 import *
import re

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

def updatemap(data):
    mapstr = PC.SEND_ARENA.findall(data)[0]
    print mapstr

dataA = ["INS\nF\n", \
"INS\n10\n",\
"INS\nL\n",\
"INS\nR\n",\
"INS\nC\n",\
"INS\nB\n"]

for i in dataA:
    a=PCtoArduinoTranslate(i)
    for x in a:
        print hex(x),
    print

updatemap("MAP somestringhere haha\n") # for rpi class

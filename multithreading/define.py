'''
This class contains only the command CONSTANTS bytes for flow control across all src within this mdp project
'''
class Android:
    NAME='ANDROID'
    ECHO_BACK= 0x3132

    EXPLORATION_MDF = 0x10  #mdf sent indicates explored or unexplored map
    OBSTACLES_MDF = 0x21    #mdf sent indicates obstacles or free grid
    
    #action command bytes from android to arduino 
    SENSE = 0XA0            
    MOVE_FORWARD = 0XA1
    ROTATE_LEFT = 0XA2
    ROTATE_RIGHT = 0XA3
    
    EXPLORE_MODE = 0xA4
    SOLVE_MAZE = 0xA5
       
class Arduino:
    NAME='ARDUINO'
    ECHO_BACK= 0x00

    # action command bytes from rpi to arduino
    SENSE = Android.SENSE
    MOVE_FORWARD = Android.MOVE_FORWARD
    ROTATE_LEFT = Android.ROTATE_LEFT
    ROTATE_RIGHT = Android.ROTATE_RIGHT

class PC:
    NAME='WIFI'
    ECHO_BACK= 0x3132

#   NO MEANINGFUL COMMAND BYTES FOR NOW   
    

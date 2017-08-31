import logging
import threading
import Queue
from WifiConnection import WifiConnection

ROBOT_READY = 0
ROBOT_BUSY = 1

def main():
    
    status = ROBOT_BUSY
    rpiQueue = Queue.Queue()
    
    logging.basicConfig(level=logging.INFO)    
    logger = logging.getLogger('mdprobot')
    
    logger.info('Starting up main program')
   
   ##start wifi thread
    logger.info('Starting up connection to PC')
    wifiQueue = Queue.Queue()
    wifiConnection = WifiConnection(wifiQueue, rpiQueue, 'localhost', 8000)
    wifiConnection.start()
    
    # start serial thread
    logger.info('Starting up connection to arduino')
    arduinoQueue = Queue.Queue()
    logger.info('Connected to arduino')
    
    # start bluetooth thread
    logger.info('Starting up connection to Nexus')
    nexusQueue = Queue.Queue()
    logger.info('Connected to Nexus')
    
    status = ROBOT_READY
    
    while (status == ROBOT_READY):
        logger.info('Awaiting instruction')
        
        if(not rpiQueue.empty()):
            status = ROBOT_BUSY
            message = rpiQueue.get(True);
            agent = message[agent]
            logger.info('Recieved message from ', agent)
            
            #if(agent == 'Arduino'):
                
            
            #if(agent == 'Android'):
            
            #if(agent == 'Arduino'):
            
        status = ROBOT_BUSY
            
        
        
if __name__ == "__main__": main()

import socket
import threading
import logging
from define import *

class WifiConnection(threading.Thread):

    host = ''   # Symbolic name, meaning all available interfaces
    port = 8888 # Arbitrary non-privileged port
    wifiInbox = None
    rpiInbox = None
    
    def __init__(self, wifiInbox, rpiInbox, ipaddr, port):
        '''constructor for wifi connection takes in queue, ipaddr and port'''
        threading.Thread.__init__(self,)
        self.host = ipaddr
        self.port = port
        self.wifiInbox = wifiInbox
        self.rpiInbox = rpiInbox
        
    def run(self):
    
        logger = logging.getLogger('mdprobot')
    
        #set up info for server
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            serverSocket.bind((self.host, self.port))
        except socket.error as msg:
            logger.error('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])

        serverSocket.listen(1)
        logger.info('Waiting for Connection on %s:%s', self.host, self.port)
        
        while True:
            #wait to accept a connection - blocking call
            conn, addr = serverSocket.accept()
            logger.info('Connected to PC')
            data = ''
            
            try: 
                conn.send('Hello')
                data = conn.recv(1024)
                logger.info(data+"\n")
            except socket.error as msg:
                logger.error(msg)
                logger.error('Disconnected')
            if not data: break
            
            conn.send(str(PC.ECHO_BACK))
             
        serverSocket.close()
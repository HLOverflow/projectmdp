import socket
import threading
from Queue import Queue
import traceback

__author__ = "Tay Hui Lian"
__doc__ = '''This is a test program with 3 TCP sockets.
1 Server (Pc) and 2 Clients (Bt and Usb)
There are in total 3+1 = 4 threads.
Each threads are used to run separate while loops
There are 3 threads for receiving data respectively.
    Once data received, data will be put into central queue
1 thread for sending data.
    allocate function will take from central queue and decide who to send.

To test this (run on linux because linux has built in netcat) :

run each command on separate terminal screens.

1) Set up 2 netcat listener at port 8001 (as bluetooth) and 8002(as usb).

nc -nlvp 8001
nc -nlvp 8002

2) python coordinator.py

3) python interactiveclient.py
enter> hi

4) At the moment... to terminate, use ps aux and kill command.
'''

class Pc(object):
    def __init__(self, queue):
        self.server = socket.socket()
        self.server.bind(('', 8000))
        self.server.listen(1)
        self.queue = queue

        try:
            self.client, self.clientaddr = self.server.accept()
        
        except Exception:
            print traceback.print_exc()
            print "disconnecting pc"
            self.disconnect()
            
    def sendData(self, data):
        self.client.send(data + "\n")

    def receiveData(self):
        print "pc receive"
        while 1:
            try:
                data = self.client.recv(2048)
            except Exception:
                traceback.print_exc()
                print "pc receivedata problem"
                break
            if(data):
                self.queue.put("From Pc:" + data)
                print "data put into queue by pc"
        self.disconnect()

    def disconnect(self):
        self.client.close()
        self.server.close()
        
class Bt(object):
    def __init__(self, queue):
        self.client = socket.socket()
        self.isConnected = False
        self.connect()
        self.queue = queue
        
    def connect(self):
        try:
            if(not self.isConnected):
                self.client.connect(("127.0.0.1", 8001))
                self.isConnected = True
                print "connected to bt at port 8001"
        except:
            self.isConnected = False
            traceback.print_exc()
            print "bt connect got problem"

    def sendData(self, data):
        self.client.send(data + "\n")

    def receiveData(self):
        while 1:
            try:
                data = self.client.recv(2048)
            except Exception:
                traceback.print_exc()
                print "bt receivedata problem. set data nothing"
                break
            if(data):
                self.queue.put("From Bt:" + data)
        self.disconnect()

    def disconnect(self):
        self.client.close()

class Usb(Bt):
    def connect(self):
        try:
            if(not self.isConnected):
                self.client.connect(("127.0.0.1", 8002))
                self.isConnected = True
                print "connected to usb at port 8002"
        except:
            self.isConnected = False
            traceback.print_exc()
            print "usb connect got problem"
    def receiveData(self):
        print "usb receive"
        while 1:
            try:
                data = self.client.recv(2048)
            except Exception:
                traceback.print_exc()
                print "usb receive data problem"
                break
            if(data):
                self.queue.put("From usb:" + data)
                print "data put into queue by usb"
        self.disconnect()

def allocate(queue, pc, bt, usb):
    try:
        while 1:
            data = queue.get()      # will get data if not empty.
            print "queue.get data: ", data
            if "From Bt:" in data:
                # pass data to Pc
                print "passing data to pc and usb"
                pc.sendData(data)
                usb.sendData(data)
            elif "From Pc:" in data:
                # pass data to Bt
                print "passing data to bluetooth and usb"
                bt.sendData(data)
                usb.sendData(data)
            elif "From Usb:" in data:
                print "passing data to pc and bluetooth"
                pc.sendData(data)
                bt.sendData(data)
            else:
                print "From unknown:", data
    except:
        traceback.print_exc()
        print "allocate got problem"

if __name__ == "__main__":

    # make a queue
    q = Queue()
    print "made a queue"
    bt_t = Bt(q)
    print "initialized bt_t"
    usb_t = Usb(q)
    print "initialized usb_t"
    pc_t = Pc(q)
    print "initialized pc_t"
    try:
        print "starting thread"
        pc_receive = threading.Thread(target=pc_t.receiveData)
        bt_receive = threading.Thread(target=bt_t.receiveData)
        usb_receive = threading.Thread(target=usb_t.receiveData)
        
        th = threading.Thread(target=allocate, args=(q, pc_t, bt_t, usb_t))
        
        pc_receive.start()
        bt_receive.start()
        usb_receive.start()
        
        th.start()
    except Exception:
        print traceback.print_exc()
        print "cannot start new thread"
        pc_t.disconnect()
        bt_t.disconnect()
        usb_t.disconnect()

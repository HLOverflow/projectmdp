import socket

s = socket.socket()
s.connect(('127.0.0.1', '8000'))
print "connected."
print "ctrl + c to abort."
data = raw_input("enter> ")
while 1:
    s.send(data + "\n")
    print "received: ", s.recv(2048)
    data = raw_input("enter> ")

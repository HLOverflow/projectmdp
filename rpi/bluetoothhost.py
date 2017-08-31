#!/usr/bin
from bluetooth import *


uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
name = "MDP-Server"

class BluetoothService(object):
	def __init__(self, uuid, AdvertisementName):
		'''constructor'''
		self.uuid = uuid
		self.AdvertisementName = AdvertisementName
		self.server_sock = BluetoothSocket(RFCOMM)

	def run(self):
		self.server_sock.bind(("", PORT_ANY))
		self.server_sock.listen(1)
		self.port = server_sock.getsockname()[1]

		# advertisement
		advertise_service( server_sock, self.AdvertisementName,
  			service_id = self.uuid,
    			service_classes = [ self.uuid, SERIAL_PORT_CLASS ],
    			profiles = [ SERIAL_PORT_PROFILE ],
    			# protocols = [ OBEX_UUID ]
 		)
		print("Waiting for connection on RFCOMM channel %d" % port)

		# establishing connection with client.
		client_sock, client_info = server_sock.accept()
		print("Accepted connection from ", client_info)

		try:
    			while True:
				# reading
        			print ("In while loop...")
                                data = client_sock.recv(1024)
        			if len(data) == 0: break		# why break?
       			print("Received [%s]" % data)

			# processing
			data = self.processData(data)

			# send back.
        		client_sock.send(data)

		except IOError:
     			pass
		except Exception:
			self.stop()		# should this be stop?
		finally:
			self.stop()		# should this be stop?

	def stop(self):
		print("disconnected")
		client_sock.close()
		server_sock.close()
		print("all done") 

	def processData(self, data):
		return data + "i am pi"


if __name__ == "__main__":
	uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
	name = "MDP-Server"

	service = BluetoothService(uuid, name)
	service.run()


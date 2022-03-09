import zmq
import time
from PyQt5.QtCore import pyqtSignal, QThread, QRunnable
import asyncio

# class ClientClass(QThread):
#     def __init__(self, parent=None):
#         super(ClientClass, self).__init__(parent)
        
#         self.context = zmq.Context()
#         self.socket = self.context.socket(zmq.REQ)
#         print("Connecting to hello world server…")
#         self.socket.connect("tcp://localhost:5555")

#     def run(self):
#         for i in range(1000):
#             print("Sending request %s …" % i)
#             self.socket.send(b"Hello Hello Hello Hello Hello hello Hello Hello Hello Hello Hello Hello Hello")

#             #  Get the reply.
#             message = self.socket.recv()
#             # print("Received reply %s [ %s ]" % (i, message))
from multiprocessing.connection import Client

class ClientClass():
    def __init__(self, parent=None):
        # super(ClientClass, self).__init__(parent)
        self.connected = False

    def connect(self):
        try:
            self.address = ('localhost', 7000)
            self.conn = Client(self.address, authkey=b'secret password')
            self.connected = True
            print("Connected")
            return True
        except:
            print("Couldn't connect")
            return False

    def disconnect(self):
        try:
            self.conn.send('close')
            self.conn.close()
            self.connected = False
            print("Disconnected")
            return True
        except:
            print("Couldn't disconnect")
            return False

    def isConnected(self):
        return self.connected

    async def sendData(self, sensor):
        quat = sensor.getOffsetQuaternion()
        sensorAsDict = {"id": sensor.id, "qw": quat[0], "qx": quat[1], "qy": quat[2], "qz": quat[3]}
        self.conn.send(sensorAsDict)

    def sendSensor(self, sensor):
        asyncio.run(self.sendData(sensor))

# class ClientClass(QThread):
#     message = pyqtSignal(str)

#     def __init__(self, parent=None):
#         super(ClientClass, self).__init__(parent)
#         self.connected = False
#         self.dataAvailable = None
#         self.index = 0

#     def connect(self):
#         self.address = ('localhost', 6000)
#         self.conn = Client(self.address, authkey=b'secret password')
#         self.connected = True

#     def run(self):
#         while True:
#             if self.dataAvailable:
#                 print("Message ", self.index, self.dataAvailable)
#                 self.conn.send(self.dataAvailable)
#                 self.index += 1
#                 self.dataAvailable = None
#             self.conn.send("")
            
            
            

#         self.conn.send('close')
#         self.conn.close()

#     def isConnected(self):
#         return self.connected

#     def sendSensor(self, sensor):
#         quat = sensor.getOffsetQuaternion()
#         sensorAsDict = {"id": sensor.id, "qw": quat[0], "qx": quat[1], "qy": quat[2], "qz": quat[3]}
#         self.dataAvailable = sensorAsDict
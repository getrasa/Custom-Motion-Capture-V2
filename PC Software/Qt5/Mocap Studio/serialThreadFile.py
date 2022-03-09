import serial
import json
import time
from PyQt5.QtCore import pyqtSignal, QThread
from mocapSensor import MocapSensor
from structures import Quaternion, Acceleration
from multiprocessing.connection import Client

class SerialThreadClass(QThread):
    message = pyqtSignal(list)
    sensorMessage = pyqtSignal(MocapSensor)
    sensorList = []
    
    def __init__(self, parent=None):
        super(SerialThreadClass, self).__init__(parent)
        self.connected = False
        self.connectedServer = False
        self.collectingData = False


    def run(self):
        while self.connected:
            try:
                text = self.serialPort.readline().decode('ascii').splitlines()[0]
                # receivedSensor = json.loads(text)
                dataList = text.split(',')
                if (not dataList[0].isdigit()): continue
                receivedSensor = {"id": dataList[0], "qw": float(dataList[1]) / 1000, "qx": float(dataList[2]) / 1000, 
                                "qy": float(dataList[3])/1000, "qz": float(dataList[4])/1000, "ax": dataList[5], "ay": dataList[6], "az": dataList[7]}

                # receivedSensor = {"id": dataList[0], "qw": float(dataList[1]) / 1000, "qx": float(dataList[2]) / 1000, 
                #                 "qy": float(dataList[3])/1000, "qz": float(dataList[4])/1000}
                
                foundSensorAtIndex = [index for index, sensor in enumerate(self.sensorList) if sensor.id == receivedSensor["id"]]
                foundSensorAtIndex = foundSensorAtIndex[0] if foundSensorAtIndex else None

                quat = [float(receivedSensor[k]) for k in ('qw', 'qx', 'qy', 'qz')]
                acc = [receivedSensor[k] for k in ('ax', 'ay', 'az')]

                if (len(quat) == 0): continue
                
                
                if isinstance(foundSensorAtIndex, int):
                    sensor = self.sensorList[foundSensorAtIndex]
                    self.sensorList[foundSensorAtIndex].setQuaternion(*quat)
                    self.sensorList[foundSensorAtIndex].setAcceleration(*acc)
                    # print([i.id for i in self.sensorList ])
                    w,x,y,z = sensor.getOffsetQuaternion()
                    # print("Ofsett:", foundSensorAtIndex, w,x,y,z)
                    if self.connectedServer:
                        sensorAsDict = {"id": sensor.id, "qw": w, "qx": x, "qy": y, "qz": z}
                        self.conn.send(sensorAsDict)

                    if self.collectingData and abs(y) >= 0.05:
                    # if self.collectingData:
                        self.sensorList[foundSensorAtIndex].addCalibrationWalkData([w, x, y, z])


                else:
                    self.sensorList.append(MocapSensor(receivedSensor["id"]))
                    self.sensorList[-1].setQuaternion(*quat)
                    # self.sensorList[-1].setAcceleration(*acc)
                    self.sensorMessage.emit(self.sensorList[-1])

                # print("RECEIVED:", receivedSensor)


                self.message.emit(self.sensorList)

            except Exception as e:
                print("Error", e)
            

    def serialWrite(self, id, request):
        print("BYTES ID", bytes([id]))
        self.serialPort.write(bytes([id]))
        print("BYTES REQUEST", request.encode())
        self.serialPort.write(request.encode())



    # SERIAL FUNCTIONS
    def connect(self, port='COM6', baudrate=1000000):
        try:
            print("Port:", port, "baudrate", baudrate)
            self.serialPort = serial.Serial()
            self.serialPort.port = port
            self.serialPort.baudrate = baudrate
            self.serialPort.open()
            self.connected = True
            print("Serial Connected")
            return True

        except:
            print("Serial Failed")
            return False

    def disconnect(self):
        try:
            self.connected = False
            self.serialPort.close()
            print("Serial Disconnected")
            return True
        except:
            print("Diconnecting Serial Failed")
            return False

    def isConnected(self): return self.connected


    # SERVER FUNCTIONS
    def connectServer(self):
        try:
            self.address = ('localhost', 2000)
            self.conn = Client(self.address, authkey=b'secret password')
            self.connectedServer = True
            print("Connected")
            return True
        except:
            print("Couldn't connect")
            return False

    def disconnectServer(self):
        try:
            self.conn.send('close')
            self.conn.close()
            self.connectedServer = False
            print("Disconnected")
            return True
        except:
            print("Couldn't disconnect")
            return False

    def isConnectedServer(self): return self.connectedServer

    # OFFSET FUNCTIONS
    def resetSensorRotation(self):
        for s in self.sensorList:
            s.setQuaternionOffsetCurrent()

    
    # CALIBRATION FUNCTIONS
    def calibrateWalk(self):
        for s in self.sensorList:
            s.calibrateWalk()
                

    def startCollectingData(self):
        self.resetCollectedData()
        self.collectingData = True

    def stopCollectingData(self):
        for i, s in enumerate(self.sensorList):
            data = s.getCollectedData()
        self.collectingData = False

    def resetCollectedData(self):
        for s in self.sensorList:
            s.resetCollectedData()

    def calculateAndApplyCalibration(self):
        for s in self.sensorList:
            s.calibrateWalk()

    def getCalibrationOffset(self):
        return [s.getCalibrationOffset() for s in self.sensorList]
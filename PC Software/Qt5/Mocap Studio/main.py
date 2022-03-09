from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore, QtGui, QtWidgets
import sys, time, asyncio
from serialThreadFile import SerialThreadClass
from clientFile import ClientClass
from mocapSensor import MocapSensor

class Ui(QtWidgets.QMainWindow):
    runButtonToggle = False
    streamButtonToggle = False
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('Mocap Controller.ui', self)
        self._translate = QtCore.QCoreApplication.translate
        self.mySerial = SerialThreadClass()
        
        # Buttons
        self.runButton.clicked.connect(self.runButtonClickedEvent)
        self.streamButton.clicked.connect(self.runStreamClickedEvent)
        self.calibrateButton.clicked.connect(lambda: asyncio.run(self.calibrateButtonClickedEvent()))
        self.collectWalkButton.clicked.connect(lambda: asyncio.run(self.collectWalkButtonClickedEvent()))
        self.calibrateWalkButton.clicked.connect(lambda: asyncio.run(self.calibrateWalkButtonClickedEvent()))

        # Connect the contextmenu
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.menuContextTree)

        # Show App
        self.show()

        
    def runButtonClickedEvent(self):
        if self.mySerial.isConnected():
            isDisconnected = self.mySerial.disconnect()
            if isDisconnected: self.runButton.setText(self._translate("MainWindow", "Run Serial"))

        else:
            isConnected = self.mySerial.connect()
            if isConnected:
                self.mySerial.start()
                self.mySerial.message.connect(self.assignValuesToTree)
                self.runButton.setText(self._translate("MainWindow", "Stop Serial"))


    def runStreamClickedEvent(self):
        if self.mySerial.isConnectedServer():
            isDisconnected = self.mySerial.disconnectServer()
            if isDisconnected: self.streamButton.setText(self._translate("MainWindow", "Stream"))

        else:
            isConnected = self.mySerial.connectServer()
            if isConnected: self.streamButton.setText(self._translate("MainWindow", "Streaming..."))

    

    async def calibrateButtonClickedEvent(self):
        await asyncio.sleep(3)
        self.mySerial.resetSensorRotation()
        print("Position Reset")

    
    async def collectWalkButtonClickedEvent(self):
        # await asyncio.run(self.calibrateButtonClickedEvent())
        await asyncio.sleep(3)
        self.mySerial.startCollectingData()
        self.collectWalkButton.setText(self._translate("MainWindow", "Getting Data"))
        print("Getting Data")
        
        await asyncio.sleep(1)
        self.mySerial.stopCollectingData()
        print("Data Saved")


    async def calibrateWalkButtonClickedEvent(self):
        self.mySerial.calibrateWalk()
        calibrationList = self.mySerial.getCalibrationOffset()
        for i, o in enumerate(calibrationList):
            print("Offset:", i , o)
        


    def assignValuesToTree(self, sensorList):
        itemCount = self.treeWidget.topLevelItem(0).childCount()
        for i, s in enumerate(sensorList):
            if (i >= itemCount):
                item = QtWidgets.QTreeWidgetItem(self.treeWidget.topLevelItem(0))
                self.treeWidget.topLevelItem(0).child(i).setText(0, self._translate("MainWindow", str(s.id)))
                self.treeWidget.topLevelItem(0).child(i).setText(1, self._translate("MainWindow", str(0)))
                self.treeWidget.topLevelItem(0).child(i).setText(2, self._translate("MainWindow", "RUN"))
            
            else:
                self.treeWidget.topLevelItem(0).child(i).setText(0, self._translate("MainWindow", str(s.id)))
                self.treeWidget.topLevelItem(0).child(i).setText(1, self._translate("MainWindow", str(s.fpsOutput)))
                self.treeWidget.topLevelItem(0).child(i).setText(2, self._translate("MainWindow", "RUN"))

    # def streamData(self, mocapSensor):
    #     if self.myClient.isConnected():
    #         self.myClient.sendSensor(mocapSensor)

    def menuContextTree(self, point):
        # Infos about the node selected.
        index = self.treeWidget.indexAt(point)
        if not index.isValid():
            return

        item = self.treeWidget.itemAt(point)
        name = item.text(0)  # The text of the node.

        # We build the menu.
        menu = QtWidgets.QMenu()
        # action = menu.addAction(name)
        action_1 = menu.addAction("Calibrate Accel")
        action_1.triggered.connect(lambda: self.calibrateAcc(name))
        action_2 = menu.addAction("Calibrate Mag")

        menu.exec_(self.treeWidget.mapToGlobal(point))

    def calibrateAcc(self, name):
        if (name.isdigit()):
            self.mySerial.serialWrite(int(name), 'A')


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
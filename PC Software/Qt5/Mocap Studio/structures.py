import numpy as np

class Quaternion():
    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def updateQuaternion(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def getQuaternionAsList(self):
        return [self.w, self.x, self.y, self.z]

class Acceleration():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def updateQuaternion(self, w, x, y, z):
        self.x = x
        self.y = y
        self.z = z

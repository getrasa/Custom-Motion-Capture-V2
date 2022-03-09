import time, math, copy
from structures import Quaternion, Acceleration
import numpy as np

class MocapSensor():
    quaternion = Quaternion(1, 0, 0, 0)
    quaternionOffset = Quaternion(1, 0, 0, 0)
    acceleration = None
    calibrationWalkData = []
    calibrationOffset = Quaternion(1, 0, 0, 0)
    fpsOutput = 0
    lastSecFrames = 0
    lastSecTime = int(round(time.time() * 1000))
    # calibrationIdList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    calibrationIdList = [7, 8, 9, 10, 11, 12]
    
    def __init__(self, sensorId):
        self.id = sensorId
        self.lastPresent = int(round(time.time() * 1000))

    def setMode(self, mode):
        self.mode = mode

    # QUATERNIONS
    def setQuaternion(self, w, x, y, z):
        self.quaternion = Quaternion(w, x, y, z)
        self.updateFPS()


    def getOffsetQuaternion(self):
        qInput = self.quaternion.getQuaternionAsList()
        qNpose = self.quaternionOffset.getQuaternionAsList()
        qCalibration = self.calibrationOffset.getQuaternionAsList()

        ## NPOSE OFFSETING

        # Extract rotation Z of qOffset
        qNposeRotationZ = self.qExtractRotationZ(qNpose)

        # Offset input by negative Z Rotation of qNpose
        qInputOffsetByNPoseZ = self.qmult(self.getQuaternionInverse(qNposeRotationZ), qInput)

        # Input that has been offset by qNpose
        qNposeOffseted = self.qmult(qInputOffsetByNPoseZ, self.getQuaternionInverse(self.qRotateByInverseZ(qNpose)))

        ## SHOULDER EXCEPTION
        # Shoulder sensors remove Y influence (shoulders rotate only up/down & front/back, not around itself therefore that dimension is not needed)
        if int(self.id) == 15 or int(self.id) == 16:
            return self.qRotateByInverseY(qNposeOffseted)

        # Don't calibrate sensors that doesn't need calibration
        if int(self.id) not in self.calibrationIdList:
            return qNposeOffseted



        ## CALIBRATION
        # Reverse Z Rotation to zero (Z=0 By Rotating -Z)
        qOffsetedZeroedZ = self.qRotateByInverseZ(qNposeOffseted)
        # print("qOffsetedZeroedZ", qOffsetedZeroedZ[0], qOffsetedZeroedZ[1], qOffsetedZeroedZ[2], qOffsetedZeroedZ[3])

        # Apply reversed calibration rotation (Z=calibration) to qOffsetedZeroedZ
        qAppliedCalibrationRotation = self.qmult(self.getQuaternionInverse(qCalibration), qOffsetedZeroedZ)
        # print("qAppliedCalibrationRotation", qAppliedCalibrationRotation[0], qAppliedCalibrationRotation[1], qAppliedCalibrationRotation[2], qAppliedCalibrationRotation[3])

        # Applied Calibration Rotation get all rotations except Z axis (Z = 0)
        qOffsetedExceptZ = self.qExtractRotationExceptZ(qAppliedCalibrationRotation)
        # print("qOffsetedExceptZ", qOffsetedExceptZ[0], qOffsetedExceptZ[1], qOffsetedExceptZ[2], qOffsetedExceptZ[3])

        # Correct Zeroed rotation with rotation of nPoseOffseted
        qCalibratedNposeOffset = self.qmult(self.qExtractRotationZ(qNposeOffseted), qOffsetedExceptZ)

        ## FEET EXCEPTION
        # Feet sensors reverse X and Y (unlike others on arms and legs these arent placed verticaly on the side but flat just like feet)
        if int(self.id) == 9 or int(self.id) == 12:
            # return list([qCalibratedNposeOffset[0], qCalibratedNposeOffset[2], qCalibratedNposeOffset[1], qCalibratedNposeOffset[3]])
            return qNposeOffseted


        # Return Calibration
        return qCalibratedNposeOffset

        # return self.qmult(self.getQuaternionInverse(qInputOffsetByNPoseZ), self.qRotateByInverseZ(self.qRotateByInverseZ(qNpose)))
        

    def setQuaternionOffsetCurrent(self):
        quaternionList = copy.deepcopy(self.quaternion.getQuaternionAsList())
        self.quaternionOffset = Quaternion(*quaternionList)


    # ACCELERATION
    def setAcceleration(self, x, y, z):
        self.acceleration = Acceleration(x, y, z)

    # FPS
    def getFpsOutput(self):
        return self.fpsOutput

    def updateFPS(self):
        self.lastSecFrames += 1
        if int(round(time.time() * 1000)) - self.lastSecTime >= 1000:
            self.fpsOutput = self.lastSecFrames
            self.lastSecFrames = 0
            self.lastSecTime = int(round(time.time() * 1000))



    # CALIBRATION
    def addCalibrationWalkData(self, data):
        if int(self.id) in self.calibrationIdList:
            self.calibrationWalkData.append(Quaternion(data[0], data[1], data[2], data[3]))
        

    def resetCollectedData(self):
        self.calibrationWalkData = []
        self.calibrationOffset = Quaternion(1, 0, 0, 0)

    def calibrateWalk(self):
        # if int(self.id) in self.calibrationIdList:
        offsetSum = 0
        for quat in self.calibrationWalkData:
            quatAsList = quat.getQuaternionAsList()
            
            result = self.calculateCalibrationOffset(self.qRotateByInverseZ(quatAsList), 100)
            offsetSum += result[3]

        zOffset = offsetSum / (len(self.calibrationWalkData) if len(self.calibrationWalkData) else 1)
        self.calibrationOffset = Quaternion(math.sqrt(1 - zOffset**2), 0, 0, zOffset)



    def calculateCalibrationOffset(self, quat, precision):
        q = [1, 0, 0, 0]
        smallest_Y = quat[2]
        result_negative = False
        
        for i in range(precision):
            q[3] = -i/100 if result_negative else i/100
            q[0] = math.sqrt(1 - q[3]**2)
            result = self.qmult(self.getQuaternionInverse(q), quat)
            
            if (abs(result[2]) > abs(quat[2])): 
                result_negative = True
                continue
                
            if (abs(result[2]) <= abs(smallest_Y)):
                smallest_Y = result[2]
            else: break
        
        return q

    def getCalibrationOffset(self): return self.calibrationOffset.getQuaternionAsList()
    def getCollectedData(self): return [s.getQuaternionAsList() for s in self.calibrationWalkData]

    # CALC FUNCTIONS
    def qmult(self, q1, q2):
        
        q1 = np.array(q1).reshape(4, 1)
        q2 = np.array(q2).reshape(4, 1)
        q3 = [0, 0, 0, 0]
        
        q3[0] = -q1[1] * q2[1] - q1[2] * q2[2] - q1[3] * q2[3] + q1[0] * q2[0]
        q3[1] =  q1[1] * q2[0] + q1[2] * q2[3] - q1[3] * q2[2] + q1[0] * q2[1]
        q3[2] = -q1[1] * q2[3] + q1[2] * q2[0] + q1[3] * q2[1] + q1[0] * q2[2]
        q3[3] =  q1[1] * q2[2] - q1[2] * q2[1] + q1[3] * q2[0] + q1[0] * q2[3]
        
        return np.array(q3).reshape(4,1)


    def qExtractRotationX(self, quat):
        q = copy.deepcopy(quat)
        q[2], q[3] = 0, 0
        mag = math.sqrt(q[0]*q[0] + q[1]*q[1])
        q[0] /= mag
        q[1] /= mag
        return q

    def qExtractRotationY(self, quat):
        q = copy.deepcopy(quat)
        q[1], q[3] = 0, 0
        mag = math.sqrt(q[0]*q[0] + q[2]*q[2])
        q[0] /= mag
        q[2] /= mag
        return q

    def qExtractRotationZ(self, quat):
        q = copy.deepcopy(quat)
        q[1], q[2] = 0, 0
        mag = math.sqrt(q[0]*q[0] + q[3]*q[3])
        q[0] /= mag
        q[3] /= mag
        return q

    def qExtractRotationExceptZ(self, quat):
        q = copy.deepcopy(quat)
        q[3] = 0
        mag = math.sqrt(q[0]*q[0] + q[1]*q[1] + q[2]*q[2])
        q[0] /= mag
        q[1] /= mag
        q[2] /= mag
        return q


    def qRotateByInverseX(self, quat):
        rotationX = self.qExtractRotationX(quat)
        return self.qmult(self.getQuaternionInverse(rotationX), quat)

    def qRotateByInverseY(self, quat):
        rotationY = self.qExtractRotationY(quat)
        return self.qmult(self.getQuaternionInverse(rotationY), quat)

    def qRotateByInverseZ(self, quat):
        rotationZ = self.qExtractRotationZ(quat)
        return self.qmult(self.getQuaternionInverse(rotationZ), quat)

    

    def getQuaternionConjugate(self, quat):
        return np.array([quat[0], -quat[1], -quat[2], -quat[3]]).reshape(4,1)

    def getQuaternionInverse(self, quat):
        return (self.getQuaternionConjugate(quat) / np.sum(np.power(quat, 2))).reshape(4,1)

    def getID(self): return self.id







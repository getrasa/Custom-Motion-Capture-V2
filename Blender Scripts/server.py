import bpy
import serial
import threading
import time
import re
import numpy as np
from mathutils import Matrix, Euler, Vector, Quaternion
from multiprocessing.connection import Listener
import math

from bpy import context
from math import degrees, radians


 
armature = bpy.data.objects['rig']
bones = armature.pose.bones


print("Imported Libraries")

## Array for storying sensor data read from serial port
## (w, x, y, z) represent quaternion rotation, (ax, ay, az) acceleration
#                   w, x, y, z,ax,ay,az
sensorDataArray = [[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]
                  ,[1, 0, 0, 0, 0, 0, 0]]


class ReceiverThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.connection = False
        
    def run(self):
        if not self.connection:
            self.address = ('localhost', 2000)     # family is deduced to be 'AF_INET'
            self.listener = Listener(self.address, authkey=b'secret password')
            self.conn = self.listener.accept()
            self.connection = True
            print('connection accepted from', self.listener.last_accepted)
            
        
        # Options
        set_location = True
        record_keyframes = False

        # FPS (Frames per second when recording)
        FPS = 30
        current_frame = 0
        tick = time.time()
        frameReady = False
        
        # Foot info
        footCurrent = "left"
        previousFootCoords = [0, 0]
            
            
        while True:
            msg = self.conn.recv()
            if msg == "": continue
            # do something with msg
            if msg == 'close':
                self.conn.close()
                self.connection = False
                break
            
            for i in msg:
                if not i.isdigit(): continue
            
            sID = int(msg["id"]) - 1
            w = msg["qw"][0]
            x = msg["qx"][0]
            y = msg["qy"][0]
            z =msg["qz"][0]
            
            sensorDataArray[sID] = [w, x, y, z]
            
            
            # RUNNING THE MAPPING
            
            
            # Ready for next frame (FPS)
            if time.time() >= tick+(1/FPS):
                frameReady = True
                
             
            # If all conditions met, begin mapping
            if self.connection and frameReady:
#                print("Id", sID, "QUAT:", [w, x, y, z])

                ##Right Arm
                upperArmRight = bones["upper_arm_fk.R"]
                forearmRight = bones["forearm_fk.R"]
                wristRight = bones["hand_fk.R"]

                
                sensorIndex = 0
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(upperArmRight, [w, x, y, z], [0, 0, 0], [-90, 0, 145])
                
                sensorIndex = 1
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(forearmRight, [w, x, y, z], [-7, 0, 0], [-90, 0, 145])
                
                sensorIndex = 2
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(wristRight, [w, x, y, z], [-7, 0, 0], [-90, 0, 155])
                
                
                
                ##Left Arm
                upperArmLeft = bones["upper_arm_fk.L"]
                forearmLeft = bones["forearm_fk.L"]
                wristLeft = bones["hand_fk.L"]
                
                sensorIndex = 3
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(upperArmLeft, [w, x, y, z], [0, 0, 0], [-90, 0, -145])
                
                sensorIndex = 4
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(forearmLeft, [w, x, y, z], [-7, 0, 0], [-90, 0, -145])
                
                sensorIndex = 5
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(wristLeft, [w, x, y, z], [-7, 0, 0], [-90, 0, -155])

                

                ## Left leg
                thighLeft = bones["thigh_fk.L"]
                shinLeft = bones["shin_fk.L"]
                footLeft = bones["foot_fk.L"]
                toesLeft = bones["toe.L"]

                sensorIndex = 6
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(thighLeft, [w, -x, -y, z], [0, 0, 0], [-94, 0, -8])
                
                sensorIndex = 7
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(shinLeft, [w, -x, -y, z], [0, 0, 0], [-85, 0, -8])
                
                sensorIndex = 8
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(footLeft, [w, -y, -x, z], [0, 0, 0], [-140, 0, 4])
                


                ## Right leg
                thighRight = bones["thigh_fk.R"]
                shinRight = bones["shin_fk.R"]
                footRight = bones["foot_fk.R"]
                toesRight = bones["toe.R"]
                
                sensorIndex = 9
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(thighRight, [w, x, y, z], [0, 0, 0], [-94, 0, 8])
                
                sensorIndex = 10
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(shinRight, [w, x, y, z], [0, 0, 0], [-85, 0, 8])
                
                sensorIndex = 11
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(footRight, [w, y, x, z], [0, 0, 0], [-140, 0, -4])


                
                ## Middle body
                hips = bones["torso"]
                chest = bones["chest"]
                leftShoulder = bones["shoulder.L"]
                rightShoulder = bones["shoulder.R"]
                head = bones["head"]

                sensorIndex = 12
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(hips, [w, y, -x, z], [0, 0, 0], [0, 0, 0])
                
                sensorIndex = 13
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(chest, [w, y, -x/2, z], [0, 0, 0], [0, 0, 0])
                
                sensorIndex = 14
                w, x, y, z = sensorDataArray[sensorIndex][:4]
#                setRotation(leftShoulder, [w, y, x, z], [0, 0, 0], [5, 0, -69])
#                setRotationLocal(leftShoulder, [w, x, -y, z])
                
                sensorIndex = 15
                w, x, y, z = sensorDataArray[sensorIndex][:4]
#                setRotation(rightShoulder, [w, -y, x, z], [0, 0, 0], [5, 0, 69])
#                setRotationLocal(rightShoulder, [w, -x, -y, z])
                
                sensorIndex = 16
                w, x, y, z = sensorDataArray[sensorIndex][:4]
                setRotation(head, [w, y, -x, z], [0, 0, 0], [90, 0, 0])
                
                
                bone_names_L = ["torso", "thigh_fk.L", "shin_fk.L", "foot_fk.L", "toe.L"]
                bone_names_R = ["torso", "thigh_fk.R", "shin_fk.R", "foot_fk.R", "toe.R"]
                
                if (set_location):
                    # Get toes location
                    locationL = get_matrix_world(armature, bone_names_L).decompose()[0]
                    locationR = get_matrix_world(armature, bone_names_R).decompose()[0]

                    # Set location left toe
#                            bones["torso"].location[0] += -locationL[0] + 0.099081
#                            bones["torso"].location[1] += -locationL[1] + 0.046848
#                            bones["torso"].location[2] += -locationL[2] + 0.030826                    
                    

                    if locationL[2] < locationR[2]:
                        if footCurrent != "left":
                            print("Turned Left")
                            print("LocationL", locationL, "LocationR", locationR)
                            footCurrent = "left"
                            previousFootCoords = [locationL[0], locationL[1]]
                        bones["torso"].location[0] -= locationL[0] - previousFootCoords[0] 
                        bones["torso"].location[1] -= locationL[1] - previousFootCoords[1] 
                        bones["torso"].location[2] -= locationL[2] - 0.030826
                        
                    else:
                        if footCurrent != "right":
                            print("Turned Right")
                            print("LocationR", locationR, "LocationL", locationL)
                            footCurrent = "right"
                            previousFootCoords = [locationR[0], locationR[1]]
                        bones["torso"].location[0] -= locationR[0] - previousFootCoords[0] 
                        bones["torso"].location[1] -= locationR[1] - previousFootCoords[1] 
                        bones["torso"].location[2] -= locationR[2] - 0.030826
                    
#                            bones["torso"].location[0] = bones["torso"].location[0] - (locationL[0] - 0.099081)

                
                    
                if (record_keyframes):    
                    # Left Arm
                    upperArmLeft.keyframe_insert(data_path="rotation_quaternion", index=-1, group="upper_arm_fk.L", frame=current_frame)
                    forearmLeft.keyframe_insert(data_path="rotation_quaternion", index=-1, group="forearm_fk.L", frame=current_frame)
                    wristLeft.keyframe_insert(data_path="rotation_quaternion", index=-1, group="hand_fk.L", frame=current_frame)   
                    
                    
                    # Right Arm
                    upperArmRight.keyframe_insert(data_path="rotation_quaternion", index=-1, group="upper_arm_fk.R", frame=current_frame)
                    forearmRight.keyframe_insert(data_path="rotation_quaternion", index=-1, group="forearm_fk.R", frame=current_frame)
                    wristRight.keyframe_insert(data_path="rotation_quaternion", index=-1, group="hand_fk.R", frame=current_frame)
                    
                    # Left leg
                    thighLeft.keyframe_insert(data_path="rotation_quaternion", index=-1, group="thigh_fk.L", frame=current_frame)
                    shinLeft.keyframe_insert(data_path="rotation_quaternion", index=-1, group="shin_fk.L", frame=current_frame)
                    footLeft.keyframe_insert(data_path="rotation_quaternion", index=-1, group="foot_fk.L", frame=current_frame)
                    
                    
                    # Right leg
                    thighRight.keyframe_insert(data_path="rotation_quaternion", index=-1, group="thigh_fk.R", frame=current_frame)
                    shinRight.keyframe_insert(data_path="rotation_quaternion", index=-1, group="shin_fk.R", frame=current_frame)
                    footRight.keyframe_insert(data_path="rotation_quaternion", index=-1, group="foot_fk.R", frame=current_frame)
                    
                    hips.keyframe_insert(data_path="rotation_quaternion", index=-1, group="torso", frame=current_frame)
                    hips.keyframe_insert(data_path="location", index=-1, group="torso", frame=current_frame)
                    chest.keyframe_insert(data_path="rotation_quaternion", index=-1, group="chest", frame=current_frame)
                    leftShoulder.keyframe_insert(data_path="rotation_quaternion", index=-1, group="shoulder.L", frame=current_frame)
                    rightShoulder.keyframe_insert(data_path="rotation_quaternion", index=-1, group="shoulder.R", frame=current_frame)
                    
                    if (current_frame > 0):
                        head.keyframe_insert(data_path="rotation_quaternion", index=-1, group="head", frame=current_frame-1)
                        
                    current_frame += 1
                
                # Wait for next frame *FPS) 
                tick = time.time()
                frameReady = False
            
            
            
        self.listener.close()
        
    def disconnect(self):
        try: 
            self.conn.close()
            self.listener.close()
            print("Disconnected")
            
        except:
            print("Disconnection failed")
            
                          


try:
    print("Start Thread")
    receiver = ReceiverThread(1, "receiverThread")
    print("Thread started")
    receiver.start()

except:
    print("Failed")
    receiver.disconnect()







# bone:             blender bone
# quaternion:      (Quaternion) raw sensor values, [w, x, y, z], second rotation

def setRotationWorldFrame(bone, quaternion):
    # Extract quaternion coordinates
    w, x, y, z = quaternion
    
    # Create quaternion matrix based on given coordinates.
    
    location, _, scale = bone.matrix.decompose()
    
    # Express as matrix
    location_matrix = Matrix.Translation(location)
    rotation = Quaternion([w, x, y, z]).to_matrix().to_4x4()
    scale_matrix = Matrix.Scale(scale[0],4,(1,0,0)) @ Matrix.Scale(scale[1],4,(0,1,0)) @ Matrix.Scale(scale[2],4,(0,0,1))
    
    # Join location, new rotation and scale matrices back together and assign it to the bone.
    bone.matrix = location_matrix @ rotation_matrix @ scale_matrix
    bone.scale[0] = 1
    bone.scale[1] = 1
    bone.scale[2] = 1
    

def toNewReferenceFrame(localQuaternion, offsetQuaternion):
    offsetInverse = getQuaternionInverse(offsetQuaternion)
    return qmult(localQuaternion, offsetInverse)



# bone:             blender bone
# quaternion:      (Quaternion) sensor values, [w, x, y, z], second rotation
# global_offset:    (Euler) global offset of coordinates, first rotation
# local_offset:     (Euler) local offset of the bone, third rotation


def setRotation(bone, quaternion, global_offset, local_offset):
    # Extract quaternion coordinates
    w, x, y, z = quaternion
    # Create quaternion matrix based on given coordinates.
    rotation = Quaternion([w, x, y, z]).to_matrix().to_4x4()
    
    
    # Create quaternion offset matrix based on Euler coordinates.
    offset_matrix  = Euler([radians(global_offset[0]), radians(global_offset[1]), radians(global_offset[2])]).to_quaternion().to_matrix().to_4x4()
    
    # Decompose current bone matrix to get it's location, rotation(not needed) and scale vectors.
    location, _, scale = bone.matrix.decompose()
    scale = Vector([1,1,1])
    
    local_offset_matrix = rotation @ Euler([radians(local_offset[0]), radians(local_offset[1]), radians(local_offset[2])]).to_quaternion().to_matrix().to_4x4()
    
    # Express as matrix
    location_matrix = Matrix.Translation(location)
    rotation_matrix = offset_matrix @ local_offset_matrix
    scale_matrix = Matrix.Scale(scale[0],4,(1,0,0)) @ Matrix.Scale(scale[1],4,(0,1,0)) @ Matrix.Scale(scale[2],4,(0,0,1))


    # Join location, new rotation and scale matrices back together and assign it to the bone.
    bone.matrix = location_matrix @ rotation_matrix @ scale_matrix
    bone.scale[0] = 1
    bone.scale[1] = 1
    bone.scale[2] = 1
    
def setRotationLocal(bone, quaternion):
    w, x, y, z = quaternion
    bone.rotation_quaternion[0] = w
    bone.rotation_quaternion[1] = x
    bone.rotation_quaternion[2] = y
    bone.rotation_quaternion[3] = z
    
def get_matrix_world(armature, parent_tree):
    matrix = Matrix().to_4x4()
    for i, bone_name in enumerate(parent_tree):
        bone_local = armature.data.bones[bone_name].matrix_local
        bone_basis = armature.pose.bones[bone_name].matrix_basis
        
        bone_inherit_rotation = armature.data.bones[bone_name].use_inherit_rotation
        
        parent_local_inverse = armature.data.bones[parent_tree[i-1]].matrix_local.inverted()
        
        if i == 0:
            matrix = bone_local @ bone_basis
            
        else:
            matrix = matrix @ parent_local_inverse @ bone_local @ bone_basis
            if not bone_inherit_rotation:
                loc, _, scale = matrix.decompose()
                rot = (bone_local @ bone_basis).to_quaternion()
                loc, rot, scale = Matrix.Translation(loc).to_4x4(), rot.to_matrix().to_4x4(), Matrix.Diagonal(scale).to_4x4()
                matrix = loc @ rot @ scale
            
            
    return matrix
    
# Functions
def qmult(q1, q2):
    q1 = np.array(q1).reshape(4, 1)
    q2 = np.array(q2).reshape(4, 1)
    q3 = [0, 0, 0, 0]

    q3[0] = -q1[1] * q2[1] - q1[2] * q2[2] - q1[3] * q2[3] + q1[0] * q2[0]
    q3[1] =  q1[1] * q2[0] + q1[2] * q2[3] - q1[3] * q2[2] + q1[0] * q2[1]
    q3[2] = -q1[1] * q2[3] + q1[2] * q2[0] + q1[3] * q2[1] + q1[0] * q2[2]
    q3[3] =  q1[1] * q2[2] - q1[2] * q2[1] + q1[3] * q2[0] + q1[0] * q2[3]

    return np.array(q3).reshape(4,1)
    
    
def getQuaternionConjugate(quat):
    return np.array([quat[0], -quat[1], -quat[2], -quat[3]]).reshape(4,1)

def getQuaternionInverse(quat):
    return (getQuaternionConjugate(quat) / np.sum(np.power(quat, 2))).reshape(4,1)


def update_matrices(obj):
    if obj.parent is None:
        obj.matrix_world = obj.matrix_basis

    else:
        obj.matrix_world = obj.parent.matrix_world * \
                           obj.matrix_parent_inverse * \
                           obj.matrix_basis
                           

def qExtractRotationZ(quat):
        q = copy.deepcopy(quat)
        q[1], q[2] = 0, 0
        mag = math.sqrt(q[0]*q[0] + q[3]*q[3])
        q[0] /= mag
        q[3] /= mag
        return q
    
def qRotateByInverseZ(q1, q2):
        rotationZ = self.qExtractRotationZ(q2)
        return self.qmult(self.getQuaternionInverse(rotationZ), q1)
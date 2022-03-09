import bpy
from bpy import context
import serial
import pickle as pickle
from mathutils import Vector


bones = bpy.data.objects['MHXX'].pose.bones

class CustomCurve(object):
    def __init__(self, data_path, array_index):
        self.data_path = data_path
        self.array_index = array_index
        self.keyframe_points = list()


with open('anim1.pkl', 'rb') as input:
    actionFCurvesLoaded = pickle.load(input)
    
    for fcurve in actionFCurvesLoaded:
        if fcurve.data_path.startswith("pose.bones"):
            try:
                tmp = fcurve.data_path.split("[", maxsplit=1)[1].split("]", maxsplit=1)
                bone_name = tmp[0][1:-1]
                keyframe_type = tmp[1][1:]
                print("Animated pose bone:", bone_name, "(%s, index %i)" % (keyframe_type, fcurve.array_index))
                
                for keyframe in fcurve.keyframe_points:
                    bpy.context.scene.frame_current = keyframe[0]
                    
                    if(keyframe_type == "location"):
                        bones[bone_name].location[fcurve.array_index] = keyframe[1]

                        
                    if(keyframe_type == "rotation_quaternion"):
                        bones[bone_name].rotation_quaternion[fcurve.array_index] = keyframe[1]
                    
                    bones[bone_name].keyframe_insert(data_path=keyframe_type, group=bone_name, index=fcurve.array_index)

            except IndexError:
                continue

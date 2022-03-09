import bpy
from bpy import context
import pickle as pickle
from mathutils import Vector



bpy.context.scene.frame_current = 1

tracks = bpy.data.objects['MHXX'].animation_data.nla_tracks

action = bpy.data.actions['Action2020']

for fcu in action.fcurves:
    print(fcu.data_path + " channel " + str(fcu.array_index))
    print(type(fcu))
    for keyframe in fcu.keyframe_points:
        print(keyframe.co) #coordinates x,y
        


class CustomCurve(object):
    def __init__(self, data_path, array_index):
        self.data_path = data_path
        self.array_index = array_index
        self.keyframe_points = list()
        
customAction = list()


for fcu in action.fcurves:
    
    fcurve = CustomCurve(fcu.data_path, fcu.array_index)
    
    print(fcu.data_path + " channel " + str(fcu.array_index))
    print(type(fcu))
    for keyframe in fcu.keyframe_points:
        fcurve.keyframe_points.append(list(keyframe.co))
        print(Vector(list(keyframe.co))) #coordinates x,y
    
    customAction.append(fcurve)
    
with open('anim1.pkl', 'wb') as handle:
    pickle.dump(customAction, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
print("CUSTOM:")

#for fcu in customAction:
#    print(fcu.data_path + " channel " + str(fcu.array_index))
#    for keyframe in fcu.keyframe_points:
#        print(keyframe)

        
    






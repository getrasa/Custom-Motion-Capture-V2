import numpy as np
import serial
import time
import re

ser = serial.Serial('COM6', baudrate="115200", timeout=1)
is_running = True
tick = None
calibration_time = 3

offset_quat = np.array([None, None, None, None])

# Functions
def qmult(q1, q2):
    q3 = [0, 0, 0, 0]
    q3[0] = -q1[1] * q2[1] - q1[2] * q2[2] - q1[3] * q2[3] + q1[0] * q2[0]
    q3[1] =  q1[1] * q2[0] + q1[2] * q2[3] - q1[3] * q2[2] + q1[0] * q2[1]
    q3[2] = -q1[1] * q2[3] + q1[2] * q2[0] + q1[3] * q2[1] + q1[0] * q2[2]
    q3[3] =  q1[1] * q2[2] - q1[2] * q2[1] + q1[3] * q2[0] + q1[0] * q2[3]

    return np.array(q3).reshape(4,1)

def getConjugate(quat):
    return np.array([quat[0], -quat[1], -quat[2], -quat[3]]).reshape(4,1)

def getInverse(quat):
    return (getConjugate(quat) / np.sum(np.power(quat, 2))).reshape(4,1)


while is_running is True:

            # Get the number of bytes in the input buffer
            # Checks if arduino sends data
            if ser.in_waiting > 0:
                try:
                    raw_data = ser.readline().strip().decode('ascii')
                    sensor_data = [float(d) for d in re.findall(r"[-+]?\d*\.\d+|\d+", raw_data)]

                    if (len(sensor_data) == 4 and tick == None):
                        tick = time.time()
                        print("Start", sensor_data, "tick:", tick)

                    if  len(sensor_data) == 4 and time.time() >= tick+calibration_time:
                        data = np.array([sensor_data[0], sensor_data[1], sensor_data[2], sensor_data[3]]).reshape(4, 1)

                        if  offset_quat.any() == None:
                            offset_quat = data


                        # print("DATA:", data)
                        print("OFFSET DATA:", qmult(data, getInverse(offset_quat)))

                except UnicodeDecodeError:
                    print("Ascii can't decode but we will continue")

                except KeyboardInterrupt:
                    is_running = False
                    ser.close()

                # except Exception as e:
                #     print("Error:", e)
                #     is_running = False
                #     ser.close()

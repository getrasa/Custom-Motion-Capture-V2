# Custom Motion Capture
### Introduction
This project started with me trying to prove to myself that I can build a motion capture suit on my own. But it ended up being probably the most challenging and satisfying project I've completed so far.
The idea was to build a device which maps human body movements to a 3d model - wirelessly and hopefully at a reasonable framerate.
Luckily, this build manages to read 17 points/joints at a whopping speed of 50fps, fully wirelessly and runs roughly 3-5 hours on a single charge.



### Showcase
Examples of the device in action.
###### Example 1
![ezgif com-gif-maker (4)](https://user-images.githubusercontent.com/21182768/157411346-16d4fb16-f659-4abd-ba81-64916bb2bffd.gif)

###### Example 2
![ezgif com-gif-maker (5)](https://user-images.githubusercontent.com/21182768/157413374-0a718f3c-9549-4cba-9a7f-0f41efe5849c.gif)



### How it works?
The system relies on 3 components hardware-wise:
- Sensors (17)
- Receiver
- Looper (Timer)

...and 2 software solutions:
- Sensor Controller App
- Server Receiver Script

**Sensor** reads its rotation (tilt) with respect to its initial orientation and then sends the data to the receiver as Quaternions. Local rotation is then translated to world rotation during software calibration.

**Receiver** reads sensor data and passes them to the computer via serial port.

**Looper** is ment to keep the sensors in sync so that radio signals don't overlap. Although the method is quite crude. Every 20 milliseconds the looper sends a signal to all sensors to begin sending data. Since each sensor has preassigned ID it begins waiting a hardcoded id * (x millis) amount of time for its turn.

**Sensor Controller** is an application I wrote using python & pyQt. Its purpose is to display which sensors are connected, what's their frame rate and run state. It's also used for calibration and streaming data to Blender.

**Server Receiver** is a python script run in Blender which reads sensory data through a local server and maps them to character armature. I've also attached a few useful scripts for saving & loading animations to a separate file.

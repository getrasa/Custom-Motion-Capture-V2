# Custom Motion Capture
### Introduction
This project started with me trying to prove to myself that I can build a motion capture suit on my own. But it ended up being probably the most challenging and satisfying project I've completed so far.
The idea was to build a device which maps human body movements to a 3d model - wirelessly and hopefully at a reasonable framerate.
Luckily, this build manages to read 17 points/joints at a whopping speed of 50fps, fully wirelessly and runs roughly 3-5 hours on a single charge.

<p float="left">
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/12b6be4e-470a-42ba-b54d-b895316d47b4" width="24.4%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/02835e01-70ef-4833-bed1-50f3205c672c" width="24.4%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/2db9c030-f9bd-4763-a94d-1dccb6a1efc2" width="24.4%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/838a2b6b-9093-455e-ab9d-de20589fcca8" width="24.4%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/ab9a52dc-1efd-40da-883a-8fff0a918135" width="24.4%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/552845e8-12a3-4481-8c90-a2015959bd43" width="24.4%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/25997b29-048d-4614-9fa8-ee2477a3a07e" width="24.4%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/622ade1c-9178-4b52-8a83-16190f56c364" width="24.4%" />
</p>

<p float="left">
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/5f511a91-fdc6-445d-b865-c5ed10683af1" width="73%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/9d48632f-6be0-487f-b101-827367bc3f41" width="26%" />
</p>






### Showcase
Examples of the device in action. (See Photos folder for more)
##### Example 1
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

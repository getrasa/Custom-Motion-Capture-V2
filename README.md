# Custom Motion Capture V2

### Abstract
Motion capture can be achieved using multiple different methods. One of the cheapest methods however is by the use of multiple 9-axis MEMS sensors attached to specific body parts. These sensors map their 'tilt' in world space to virtual characters body parts accurately approximating movement in 3D space. This README briefly describes my own design, hardware, and software implementation of this motion capture method. 



<p float="left">
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/928f6361-6b4b-449d-99cb-8fa7410e9e91" width="73%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/4611d530-c071-47aa-912b-8a0bd0bb1ed1" width="26.3%" />
</p>

> Motion Capture V1 (wireless) vs Motion Capture V2 (wireless)





### Introduction
This project is a second, wireless, iteration of my previous Custom-Made Motion Capture system. The previous solution was wired, heavily bound by the limited computational power of an Arduino Uno and poor implementation of signal interrupts. It only managed to support 6 sensors at 10 fps which was far from practical and greatly failed to reach my expectations of a minimum 30fps threshold which is why the second version has been developed.

Custom Motion Capture V2 consists of 17 sensors strategically placed on 17 locations on the body (inspired by XSense solution) capable of reading at a whopping speed of 50fps, fully wirelessly and runs roughly 3-5 hours on a single charge.
##### Showcase
<p float="left">
  <img src="https://user-images.githubusercontent.com/21182768/157411346-16d4fb16-f659-4abd-ba81-64916bb2bffd.gif" width="49%" />
  <img src="https://user-images.githubusercontent.com/21182768/157413374-0a718f3c-9549-4cba-9a7f-0f41efe5849c.gif" width="49%" />
</p>

### Hardware Assembly Process
After a working prototype has been finalized I proceeded to design a CAD design in Fusion 360. During the design process I prioritized compactness. Small size was critical to ensure that the device doesn't obstruct subject's movement. The solution I came up with was a 3 layer sandwich of trays which slid into a case one on top the other. Sitting at the very bottom was the battery, followed by the MEMS sensor neighboring a battery charger in the second layer, finishing with an 16Mhz and wireless antenna in the final layer. The position of the battery was crucial in order to minimize vibration as it was the heaviest part of the device. I also ensured the MEMS sensor is as close to the battery as it basically was the center of gravity for our tiny sensor. 

The finished sensors were small and compact and could easily be attached to the subject with Velcro.

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

### Software Implementation

<p float="left">
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/5f511a91-fdc6-445d-b865-c5ed10683af1" width="73%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/9d48632f-6be0-487f-b101-827367bc3f41" width="26%" />
</p>





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

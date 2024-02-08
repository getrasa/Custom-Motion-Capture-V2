# Custom Motion Capture V2

### Abstract
Motion capture can be achieved using various methods. One of the most affordable, however, is by using multiple 9-axis MEMS sensors attached to strategic locations on the body. The data procured from these sensors are interpreted as orientation changes, or 'tilt', in world space, which then allows us to translate these tilts onto a virtual character's anatomy, accurately approximating movement in 3D space. 

This README briefly describes my own **design, hardware, and software implementation** of this motion capture method.



<p float="left">
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/928f6361-6b4b-449d-99cb-8fa7410e9e91" width="72%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/4611d530-c071-47aa-912b-8a0bd0bb1ed1" width="26%" />
</p>

> Motion Capture V1 (wireless) vs Motion Capture V2 (wireless)





### Introduction
This project is a second, wireless iteration of my previous custom-made motion capture system. The former solution was wired, constrained by the limited computational power of an Arduino Uno, and by a poor implementation of signal interrupts. It managed to support only 6 sensors at 10 fps, which was far from practical and fell short of my expectation for a minimum 30 fps threshold. This is why the second version has been developed.

Custom Motion Capture V2 consists of 17 sensors strategically placed at 17 locations on the body (inspired by the Xsens solution), capable of reading at an impressive speed of 50 fps, fully wirelessly, and runs for roughly 3-5 hours on a single charge.
##### Showcase
Giffs take quite a while to load...
<p float="left">
  <img src="https://user-images.githubusercontent.com/21182768/157411346-16d4fb16-f659-4abd-ba81-64916bb2bffd.gif" width="99%" />
  <img src="https://user-images.githubusercontent.com/21182768/157413374-0a718f3c-9549-4cba-9a7f-0f41efe5849c.gif" width="99%" />
</p>

### Hardware Assembly Process
After finalizing a working prototype, I proceeded to design a CAD model in Fusion 360.

During the design process, I prioritized compactness. A small size was critical to ensure that the device didn't obstruct the subject's movement. The solution I came up with was a three-layer sandwich of trays that slid into a case, one on top of the other. Sitting at the very bottom was the battery, followed by the MEMS sensor next to a battery charger in the second layer, and finishing with a 16 MHz Arduino Mini and wireless antenna in the final layer. The position of the battery was crucial to minimize vibration as it was the heaviest part of the device. I also ensured the MEMS sensor was as close to the battery as possible, as it essentially was the center of gravity for our tiny sensor.



<p float="left">
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/12b6be4e-470a-42ba-b54d-b895316d47b4" width="32%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/02835e01-70ef-4833-bed1-50f3205c672c" width="32%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/2db9c030-f9bd-4763-a94d-1dccb6a1efc2" width="32%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/838a2b6b-9093-455e-ab9d-de20589fcca8" width="32%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/ab9a52dc-1efd-40da-883a-8fff0a918135" width="32%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/552845e8-12a3-4481-8c90-a2015959bd43" width="32%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/25997b29-048d-4614-9fa8-ee2477a3a07e" width="32%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/db8a1d8c-758f-40cb-a36e-ad8aedbbaf90" width="32%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/622ade1c-9178-4b52-8a83-16190f56c364" width="32%" />
</p>

> The finished sensors were small, compact, and could easily be attached to the subject with Velcro.

### Parts
To reduce the price I sourced most of my parts from Aliexpress. The total price for all parts including spares came to around 300 aud:
- 17x 16MHz Arduino Mini
- 17x MPU 9250
- 17x TP4056 Lithium Battery Charging Module
- 17x 3.7v 500mAh Lithium Polymer Battery
- 17x NRF24L01+ Small Module
- 2x NRF24L01+ Larger with antenna
- 1x Arduino UNO
- 1x ESP32 Wroom

<p float="left">
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/90930e70-26c4-474e-ae4c-f52c0983e818" width="99%" />
</p>

> Not all components used are on the photo 


### Software Implementation
Software had to be developed not only for the sensors but also for the following:
- Blender Character Script: A client which reads all broadcasted data by the server and maps sensor tilt to character bones in real-time.
<p float="left">
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/5f511a91-fdc6-445d-b865-c5ed10683af1" width="72%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/9d48632f-6be0-487f-b101-827367bc3f41" width="25.4%" />
</p>  

> Blender script which fetches sensor values from a local server and maps them to character bones. 

- Synchronization Looper: An external clock running at 50 fps which broadcasts a "Start of the frame" signal to all connected devices. Its purpose was to ensure that all devices worked in sync and didn't overlap each other.
- Antenna Receiver: Tasked with reading and forwarding sensor data to the Sensor Manager App via a serial bus.
- Sensor Manager App: A user interface for informing the user of what sensors are connected, how they are performing, and for forwarding the data to clients via a local server.
<p float="left">
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/989ab4b0-fdba-4599-a558-9b12364c1bd2" width="30.1%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/10cb68d4-720b-44db-9643-a5b6b1751f6e" width="30.1%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/5fa37d38-6a96-4b25-8744-c85b6a77d7e7" width="36%" />
</p>  

> A Synchronisation Looper, Antenna Receiver, and Sensor Manager App consecutively.

### System Limitations
Difficult to calibrate, drifts overtime, error of around 2-3 degrees. Also, the straps are quite uncomfortable.

### Version 3?
Work on Version 3 has already begun; however, due to a severe microcontroller shortage, I am having great difficulties acquiring the required components. Without components, I can't build prototypes, making it impossible to continue. Therefore, work on Version 3 is on hold indefinitely.

I will, however, post my progress in case someone is interested.

Version 3 was not only going to be wireless but also much smaller (50% size reduction) due to it being a custom-designed PCB with surface-mounted components. I've made some progress but, as I said, nothing can be proven without a working prototype. My first shot at schematics and a very crude component placement looks as follows. This is by no means a final product, just a prototype.
<p float="left">
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/e376c53c-12de-48e5-ba64-f684a0b33a97" width="100%" />
</p> 
<p float="left">
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/04bfd11e-18ef-47a7-be55-5979e0813c9c" width="49%" />
  <img src="https://github.com/getrasa/Custom-Motion-Capture/assets/21182768/b35a9151-7bd2-494d-9aea-ab6afcc4a335" width="49%" />
</p>  

The estimated specs of this systems are predicted to be:
- Form factor reduced by 50% 
- 0.5 degree of error
- Easily 70fps bound only by wireless communication bandwidth. However, the device itself could definitely output twice as much.
- 7 to 8 hours of battery life


### Summary
The system relies on 3 components hardware-wise:
- Sensors (17)
- Receiver
- Looper (Timer)

...and 2 software solutions:
- Sensor Manager App
- Blender Character Script

**Sensor** reads its rotation (tilt) with respect to its initial orientation and then sends the data to the receiver as Quaternions. Local rotation is then translated to world rotation during software calibration.

**Receiver** reads sensor data and passes them to the computer via serial port.

**Looper** is ment to keep the sensors in sync so that radio signals don't overlap. Although the method is quite crude. Every 20 milliseconds the looper sends a signal to all sensors to begin sending data. Since each sensor has a preassigned ID it begins waiting a hardcoded id * (x millis) amount of time for its turn.

**Sensor Manager App** is an application I wrote using python & pyQt. Its purpose is to display which sensors are connected, what's their frame rate and run state. It's also used for calibration and streaming data to clients (Blender) via a local server.

**Blender Character Script** is a python script run in Blender which reads sensory data through a local server and maps them to character armature. I've also attached a few useful scripts for saving & loading animations to a separate file.




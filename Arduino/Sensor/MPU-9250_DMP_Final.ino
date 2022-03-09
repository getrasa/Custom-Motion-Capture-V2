#include "I2Cdev.h"
#include "MPU9250_9Axis_MotionApps41.h"
#include <EEPROM.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <EEPROM.h>

#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

MPU9250 mpu;

#define LED_PIN 13 // (Arduino is 13, Teensy is 11, Teensy++ is 6)
bool blinkState = false;

// MPU control/status vars
bool dmpReady = false;  // set true if DMP init was successful
uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64]; // FIFO storage buffer
float f_mag[3];         // данные магнитометра после преобразования согласно даташиту
float d_mag[4];
int16_t xGCal, yGCal, zGCal, xACal, yACal, zACal, xMCal, yMCal, zMCal;

// orientation/motion vars
Quaternion q;           // [w, x, y, z]         quaternion container
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]            gravity vector
// VectorFloat v_mag;      // [x, y, z]            вектор магнитного поля
int16_t mag[3];         // сырые данные магнитометра
Quaternion q_mag;       // вспомогательный кватернион магнитометра

int value = 0;
float voltage;
float perc;

int8_t sensorId;

//struct Data
//{
//  int8_t sensorId;
//  int8_t qW;
//  int8_t qX;
//  int8_t qY;
//  int8_t qZ;
//  int16_t aX;
//  int16_t aY;
//  int16_t aZ;
//};

struct Data
{
  int8_t sensorId;
  int16_t qW;
  int16_t qX;
  int16_t qY;
  int16_t qZ;
  int16_t aX;
  int16_t aY;
  int16_t aZ;
};

struct Request
{
  int8_t sensorId;
  char requestType;
};


Data data;
Request request;
Request emptyRequest;

RF24 radio(8, 10); // CE, CSN
//byte address[6] = "00001";

int32_t time_start;
int time_log;
int time_run;
bool readRadio = true;


const byte address[6][6] = {"00000", "00001", "00010", "00011", "00100", "00101"};
String modes[4] = {"RUN", "SLEEP", "CALIBRATE_ACC", "CALIBRATE_MAG"};
String mode = "CALIBRATE_ACC";

// ================================================================
// ===                      INITIAL SETUP                       ===
// ================================================================

void setup() {
    // join I2C bus (I2Cdev library doesn't do this automatically)
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
        Wire.setClock(400000); // 400kHz I2C clock. Comment this line if having compilation difficulties
    #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
    #endif
    
    Serial.begin(38400);
    while (!Serial); // wait for Leonardo enumeration, others continue immediately

    sensorId = EEPROM.read(0);
    EEPROM.get(4, xGCal);
    EEPROM.get(8, yGCal);
    EEPROM.get(12, zGCal);
    EEPROM.get(16, xACal);
    EEPROM.get(20, yACal);
    EEPROM.get(24, zACal);
    EEPROM.get(28, xMCal);
    EEPROM.get(32, yMCal);
    EEPROM.get(36, zMCal);
    
    Serial.print("ID:"); Serial.println(sensorId);
    Serial.print("xGCal:"); Serial.println(xGCal);
    Serial.print("yGCal:"); Serial.println(yGCal);
    Serial.print("zGCal:"); Serial.println(zGCal);
    Serial.print("xACal:"); Serial.println(xACal);
    Serial.print("yACal:"); Serial.println(yACal);
    Serial.print("zACal:"); Serial.println(zACal);

    mpu.initialize();
    mpu.testConnection();

    // wait for ready
     while (Serial.available() && Serial.read()); // empty buffer
     while (Serial.available() && Serial.read()); // empty buffer again

    // load and configure the DMP
    devStatus = mpu.dmpInitialize();

    // supply your own gyro offsets here, scaled for min sensitivity
    mpu.setXGyroOffset(xGCal);
    mpu.setYGyroOffset(yGCal);
    mpu.setZGyroOffset(zGCal);
    mpu.setXAccelOffset(xACal);
    mpu.setYAccelOffset(yACal);
    mpu.setZAccelOffset(zACal);
   
    // make sure it worked (returns 0 if so)
    if (devStatus == 0) {
        mpu.CalibrateAccel(10);
        mpu.CalibrateGyro(10);
        mpu.setDMPEnabled(true);
        dmpReady = true;

        // get expected DMP packet size for later comparison
        packetSize = mpu.dmpGetFIFOPacketSize();
        Serial.print("Packet: "); Serial.println(packetSize);
    } else {
         Serial.print(F("DMP Initialization failed (code ")); Serial.println(devStatus);
    }

    // configure LED for output
    pinMode(LED_PIN, OUTPUT);

    mpu.PrintActiveOffsets();

    // Radio Setup
    radio.begin();
    radio.setPayloadSize(15);
    radio.openWritingPipe(address[1]);
    radio.openReadingPipe(1, address[2]);
    radio.setPALevel(RF24_PA_HIGH);
    radio.setDataRate(RF24_2MBPS);
    radio.setChannel(107);
    radio.setRetries(0,1);
    radio.setAutoAck(false); 
    radio.startListening();
//    radio.stopListening();
    
    data.sensorId = sensorId;
    time_start = micros();
    time_run = millis();
    Serial.println("Listening...");
}




// ================================================================
// ===                    MAIN PROGRAM LOOP                     ===
// ================================================================

void loop() {
    // if programming failed, don't try to do anything
    if (!dmpReady) return;


    // LISTEN FOR REQUEST
    if (readRadio && radio.available()) {
      radio.read(&request, sizeof(request));
//      Serial.println("REQUEST");

      if (request.requestType != 'R') {
        Serial.println(request.sensorId);
        Serial.println(request.requestType);
      }
      // Substitute variables
      char req = request.requestType;
      int8_t sID = request.sensorId; 
      request = emptyRequest;
      time_start = micros();
      

      // Check id matches ours (ID of 0 is a request for all sensors)
      if (sID != 0 && sID != sensorId) return;

      // Set Mode
      if (req == 'R') mode = "RUN";
      if (req == 'A') mode = "CALIBRATE_ACC";
      if (req == 'M') mode = "CALIBRATE_MAG";

      // Disable listening in order to be able to write.
      radio.stopListening();
      readRadio = false;
    }
    // If no request and radio ready don't continue.
    else if (readRadio) return;


    if (mode == "RUN") {
        // SENSOR ID LESS THAN 8
        // If time has passed send message, only then read dmp data
        if (sensorId < 8 && micros() - time_start < (sensorId - 1)*1000 * 1) return;
        else if (sensorId < 8) {
          radio.write(&data, sizeof(data)); 
//          Serial.print("Write: "); Serial.println((micros() - time_start) / 1000);
//          Serial.print("Time_run"); Serial.println(millis() - time_run);
          time_run = millis();
          readRadio = true;
          radio.startListening();
        }

        // SENSOR ID GREATER THAN 8
        // Get the data before time has passed then send the message
        if (sensorId >= 8 && micros() - time_start >= (sensorId - 1)*1000 * 1) {
          radio.write(&data, sizeof(data)); 
          readRadio = true;
          radio.startListening();
        }
        // Reading from DMP takes 4-5mills, ensure master doesn't read 5 mills before time.
        if (sensorId >= 8 && micros() - time_start >= 1000*5) return;


        // CONTINUE WITH THE DMP 
        // get Initialization status
        mpuIntStatus = mpu.getIntStatus();
  
        // get current FIFO count
        fifoCount = mpu.getFIFOCount();
    
        // check for overflow (this should never happen unless our code is too inefficient)
        if ((mpuIntStatus & 0x10) || fifoCount == 1024) {
            mpu.resetFIFO();
            Serial.println(F("FIFO overflow!"));
    
        // otherwise, check for DMP data ready interrupt (this should happen frequently)
        } else if (mpuIntStatus & 0x02) {
            // wait for correct available data length, should be a VERY short wait
            while (fifoCount < packetSize) fifoCount = mpu.getFIFOCount();
            // read a packet from FIFO

            mpu.getFIFOBytes(fifoBuffer, packetSize);
            
            // track FIFO count here in case there is > 1 packet available
            // (this lets us immediately read more without waiting for an interrupt)
            fifoCount -= packetSize;
    
            // display quaternion values in easy matrix form: w x y z
            mpu.dmpGetQuaternion(&q, fifoBuffer);
            mpu.dmpGetAccel(&aa, fifoBuffer);
            mpu.dmpGetGravity(&gravity, &q);
            mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
            mpu.dmpGetLinearAccelInWorld(&aaWorld, &aaReal, &q);

//            mpu.dmpGetMag(mag, fifoBuffer);                     // получение сырых данных из DMP
//            f_mag[0] = mag[1]*((asax-128)*0.5/128+1);           // преобразование и
//            f_mag[1] = mag[0]*((asay-128)*0.5/128+1);           // замена ориантаций осей X,Y,Z по спецификации 
//            f_mag[2] = -mag[2]*((asax-128)*0.5/128+1);          // на датчик страница 38
//            VectorFloat v_mag(f_mag[0], f_mag[1], f_mag[2]);    // создаем вектор магнитометра
//            v_mag = v_mag.getNormalized();                      // нормализуем вектор
//            v_mag = v_mag.getRotated(&q_mag);                   // поворачиваем
//            float phi = atan2(v_mag.y, v_mag.x)/3.1416;         // получаем значения угла в радианах между X, Y
//            Quaternion q_mag(0.1*phi, 0, 0, 1);                 // создаем коррекционный кватернион
//            q = q_mag.getProduct(q);                            // перемножаем кватернионы для коррекции основного
//            q.normalize();   
            
            data.qW = int(q.w * 1000);
            data.qX = int(q.x * 1000);
            data.qY = int(q.y * 1000);
            data.qZ = int(q.z * 1000);
            
            
            data.aX = aaWorld.x;
            data.aY = aaWorld.y;
            data.aZ = aaWorld.z;
        }
    }

    if (mode == "CALIBRATE_ACC") {
        Serial.println("Calibrate Acc/Gyro");
        mpu.CalibrateAccel(10);
        mpu.CalibrateGyro(10);
        xGCal = mpu.getXGyroOffset();
        yGCal = mpu.getYGyroOffset();
        zGCal = mpu.getZGyroOffset();
        xACal = mpu.getXAccelOffset();
        yACal = mpu.getYAccelOffset();
        zACal = mpu.getZAccelOffset();
        EEPROM.put(4, xGCal);
        EEPROM.put(8, yGCal);
        EEPROM.put(12, zGCal);
        EEPROM.put(16, xACal);
        EEPROM.put(20, yACal);
        EEPROM.put(24, zACal);
        mpu.PrintActiveOffsets();
        mode = "RUN";

        readRadio = true;
        radio.startListening();
    }

    if (mode == "CALIBRATE_MAG") {
        mpu.CalibrateAccel(50);
        mpu.CalibrateGyro(50);
        mode = "RUN";

        readRadio = true;
        radio.startListening();
    }
}


#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
//#include <AltSoftSerial.h>


//RF24 radio(7, 10); // CE, CSN
RF24 radio(12,5);  // CE, CSN
byte address[6][6] = {"00000", "00001", "00010", "00011", "00100", "00101"};

//AltSoftSerial altSerial;

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

struct __attribute((__packed__)) Data
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

Data sData;
Request request;
Request emptyRequest;

int32_t time_go;
int requestId;
char requestType;

void setup() {
  Serial.begin(1000000);
//  altSerial.begin(9600);
//  Serial.begin(74880);
  radio.begin();
  radio.setPayloadSize(sizeof(sData));
  radio.openWritingPipe(address[1]);
  radio.openReadingPipe(1, address[1]);
  radio.setPALevel(RF24_PA_HIGH);
  radio.setDataRate(RF24_2MBPS);
  radio.setChannel(107);
  radio.setRetries(0,0);
  radio.setAutoAck(false);
 
  radio.startListening();
//  radio.stopListening();
  Serial.println("Listening...");
  Serial.println(sizeof(sData));
}
void loop() {
  
  if (Serial.available()) {
    char buf[2];
    while (Serial.available()) {
      Serial.readBytes(buf, 2);
    }
//    Serial.print(buf[0]); Serial.print(",");
//    Serial.println(buf[1]);
//    altSerial.print(buf[0]);
//    altSerial.print(buf[1]);
  }
  
  if (radio.available()) {
    radio.read(&sData, sizeof(sData));
    sendQuat();
  }
}

void sendQuat() {
  Serial.print(sData.sensorId); Serial.print(",");
  Serial.print(sData.qW); Serial.print(",");
  Serial.print(sData.qX); Serial.print(",");
  Serial.print(sData.qY); Serial.print(",");
  Serial.print(sData.qZ); Serial.print(",");
  Serial.print(sData.aX); Serial.print(",");
  Serial.print(sData.aY); Serial.print(",");
  Serial.println(sData.aZ);
}

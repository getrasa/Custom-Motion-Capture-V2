
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(7, 8); // CE, CSN
byte address[6][6] = {"00000", "00001", "00010", "00011", "00100", "00101"};

struct Data
{
  int8_t sensorId;
  int8_t qW;
  int8_t qX;
  int8_t qY;
  int8_t qZ;
  int16_t aX;
  int16_t aY;
  int16_t aZ;
};

struct Request
{
  int8_t sensorId = 0;
  char requestType = 'R';
};

Data data;
Request request;

int32_t time_start;

void setup() {
  Serial.begin(38400);
  altSerial.begin(9600);
  radio.begin();
  radio.setPayloadSize(15);
  radio.openWritingPipe(address[2]);
  radio.setPALevel(RF24_PA_HIGH);
  radio.setDataRate(RF24_2MBPS);
  radio.setChannel(107);
  radio.setRetries(0,0);
  radio.setAutoAck(false);
 
  radio.stopListening();
  Serial.println("Listening...");
  time_start = millis();
}
void loop() {
  
  if (millis() - time_start >= 20) 
  {
    radio.write(&request, sizeof(request));
    time_start = millis();
    Serial.println("S");
  }
}

#include <Wire.h>

#define I2C_ADDRESS 0x1c
#ifndef I2C_ADDRESS
#error Set i2c address with -DI2C_ADDRESS=0x1c
#endif

uint8_t pinToSend = -1;

void receiveEvent(int n) {
  uint8_t code = Wire.read();
  if (code < 64) {
    bool valueToWrite = code >= 32;
    uint8_t pinNum = code % 32;
    if (pinNum >= 2 && pinNum < A4) {
      pinMode(pinNum, OUTPUT);
      digitalWrite(pinNum, valueToWrite);
    } else {
      Serial.print("Pin # out of range: ");
      Serial.println(pinNum);
    }
  } else if (code < 64 + A4) {
    pinToSend = code - 64;
  } else {
    Serial.print("Recieved unknown code ");
    Serial.println(code);
  }
}

void requestEvent() {
  pinMode(pinToSend, INPUT_PULLUP);
  uint8_t pinVal = digitalRead(pinToSend);
  Wire.write(pinVal);
}

void setup() {
  Serial.begin(115200);
  Serial.println("Good morning!");

  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
}

void loop() {
  //Serial.println("Looping");
  delay(500);
}


#include <Wire.h>

#ifndef I2C_ADDRESS
#error Set i2c address with -DI2C_ADDRESS=0x1c
#endif

uint8_t portToSend = -1;

void receiveEvent(int n) {
    uint8_t recv = Wire.read();
    if (recv >= 100) {
        portToSend  = recv-100;
        Serial.print("setting portToSend to ");
        Serial.println(portToSend);
    } else {
        uint8_t state = recv >= 32;
        uint8_t pinNum = state? recv-32 : recv;
        Serial.print("Writing pin ");
        Serial.print(pinNum);
        Serial.print(state ? " high" : " low");

        if (pinNum >= 2 && pinNum < A4) {
            pinMode(pinNum, OUTPUT);
            digitalWrite(pinNum, state);
            Serial.println();
        } else {
            Serial.println("Error: pin not in range");
        }
    }
}

void requestEvent() {
    // Wire.write(0xfa);
    // Wire.write(0xfb);
    // Wire.write(0xfc);
    // Wire.write(0xfd);
    // Wire.write(0xfe);
    uint8_t tosend = 0;
    switch(portToSend) {
    case 0:
        tosend = PIND;
        break;
    case 1:
        tosend = PINB;
        break;
    case 2:
        tosend = PINC;
        break;
    default:
        Serial.print("Invalid port : ");
        Serial.println(portToSend);
    }
    //Wire.write(tosend);
    Serial.print("Got a request. Sending port number ");
    Serial.print(portToSend);
    Serial.print(" which is ");
    Serial.println(tosend, BIN);
    // Wire.write(tosend);
    Serial.println("Writing ");
    Serial.println(0xff, BIN);
    Wire.write(0xff);





    //Wire.write(PORTB);
    //uint8_t pinNum = Wire.read();
    //pinMode(pinNum, INPUT);

    //Serial.print("Reading pin ");
    //Serial.print(pinNum);
    //if (pinNum >= 2 && pinNum < A4) {
    //    bool state = digitalRead(pinNum);
    //    Wire.write(state);
    //    Serial.println(state ? " high" : " low");
    //} else {
    //    Serial.println("Error: pin not in range");
    //}
}

void setup() {
    Serial.begin(115200);
    Serial.println("Good morning!");
    for (int pin=2; pin<18; ++pin) {
        pinMode(pin, INPUT_PULLUP);
    }

    Wire.begin(I2C_ADDRESS);
    Wire.onReceive(receiveEvent);
    Wire.onRequest(requestEvent);
}

void loop() {
    Serial.println("Looping");
    delay(500);
}


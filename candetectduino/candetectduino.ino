#include <Wire.h>

const uint8_t i2c_address = 0x1d;
const uint8_t can_sensor_pins[8] = {11, 10, 14, 12, 16, 15, 13, 17};

// Don't expect to receive anything from the pi
void receiveEvent(int n) {
  if (true) {
    Serial.print("Received an unexpected number of bytes: ");
    Serial.println(n);
    return;
  }
}

// Cache the state of all the can sensors
uint8_t can_sensor_states = 0;

void requestEvent() {
  Wire.write(can_sensor_states);
}

void setup() {
  Serial.begin(115200);
  Serial.print("Good morning! I'm the arduino sensing cans, and my i2c "
               "address is ");
  Serial.println(i2c_address);

  // Setup GPIO pins
  for (uint8_t i=0; i<8; ++i) {
    pinMode(can_sensor_pins[i], INPUT_PULLUP);
  }

  // Setup I2C
  Wire.begin(i2c_address);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
}

void loop() {
  // Cache the soda sensor states
  uint8_t new_sensor_states = 0;
  for (uint8_t i=0; i<8; ++i) {
    new_sensor_states |= !digitalRead(can_sensor_pins[i]) << i;
  }
  can_sensor_states = new_sensor_states;
}


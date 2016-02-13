const uint8_t can_sensor_pins[8] = {11, 10, 14, 12, 16, 15, 2, 17};

void setup() {
  Serial.begin(9600);

  // Setup GPIO pins
  for (uint8_t i=0; i<8; ++i) {
    pinMode(can_sensor_pins[i], INPUT_PULLUP);
  }
}

void loop() {
  // Cache the soda sensor states
  uint8_t can_sensor_states = 0;
  for (uint8_t i=0; i<8; ++i) {
    can_sensor_states |= !digitalRead(can_sensor_pins[i]) << i;
  }
  Serial.write(can_sensor_states);
}


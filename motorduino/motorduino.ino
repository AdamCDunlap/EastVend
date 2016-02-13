const uint8_t motor_pins[8] = {2, 3, 8, 9, 4, 5, 6, 7};
const uint8_t motor_switch_pins[8] = {18, 14, 17, 16, 12, 15, 10, 11};

void setup() {
  Serial.begin(9600);

  // Setup GPIO pins
  for (uint8_t i=0; i<8; ++i) {
    pinMode(motor_switch_pins[i], INPUT_PULLUP);
    pinMode(motor_pins[i], OUTPUT);
  }
}

void loop() {
  uint8_t motor_switch_states = 0;
  for (uint8_t i=0; i<8; ++i) {
    motor_switch_states |= !digitalRead(motor_switch_pins[i]) << i;
  }

  // The type of soda we are dispensing, or 0 if none
  static uint8_t dispensingMotor = 0;

  int recv;
  if (Serial.available()) {
    recv = Serial.read();
    dispensingMotor = recv+1;
  }

  // Build up which motors should be on
  // If the switch is pressed, turn on the corresponding motor
  uint8_t motor_states = motor_switch_states;

  // If we are supposed to dispense something, also turn on the motor
  if (dispensingMotor > 0) {
    
    // If the correct bit in motor_states is already set, that means the switch
    // is pressed already, so the above loop wil take care of dispensing the
    // soda the rest of the way
    if ( !(motor_states & (1 << (dispensingMotor - 1))) ) {
      motor_states |= 1 << (dispensingMotor - 1);
    } else {
      dispensingMotor = 0;
    }
  }

  // Actually set the GPIO pins to be what we want them to be
  for (uint8_t i=0; i<8; ++i) {
    digitalWrite(motor_pins[i], motor_states & (1 << i));
  }
}


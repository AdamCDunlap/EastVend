#include <Wire.h>

const uint8_t i2c_address = 0x1c;
const uint8_t motor_pins[8] = {2, 3, 8, 9, 4, 5, 6, 7};
// const uint8_t motor_switch_pins[8] = {16, 17, 13, 12, 15, 10, 11};
const uint8_t motor_switch_pins[8] = {13, 14, 17, 16, 12, 15, 10, 11};

// The type of soda we are dispensing, or 0 if none
uint8_t dispensingMotor = 0;


// When the pi sends this arduino a byte, it should be 0-7, representing which
// type of soda to dispense
void receiveEvent(int n) {
  if (n != 1) {
    Serial.print("Received an unexpected number of bytes: ");
    Serial.println(n);
    return;
  }

  uint8_t recv = Wire.read();
  if (recv < 7) {
    dispensingMotor = recv+1;
  } else {
    Serial.print("Received a byte that I don't know how to deal with: ");
    Serial.println(recv);
  }
}

// Cache the state of all the motor switches
uint8_t motor_switch_states = 0;

void requestEvent() {
  Wire.write(motor_switch_states);
}

void setup() {
  Serial.begin(115200);
  Serial.print("Good morning! I'm the arduino driving the motors, and my i2c "
               "address is ");
  Serial.println(i2c_address);

  // Setup GPIO pins
  for (uint8_t i=0; i<8; ++i) {
    pinMode(motor_switch_pins[i], INPUT_PULLUP);
    pinMode(motor_pins[i], OUTPUT);
  }

  // Setup I2C
  Wire.begin(i2c_address);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
}

void loop() {
  // Cache the motor switch states
  uint8_t new_switch_states = 0;
  for (uint8_t i=0; i<8; ++i) {
    new_switch_states |= !digitalRead(motor_switch_pins[i]) << i;
  }
  motor_switch_states = new_switch_states;

  // Build up which motors should be on
  uint8_t motor_states = 0;

  // If the switch is pressed, turn on the corresponding motor
  for (uint8_t i=0; i<8; ++i) {
    if (motor_switch_states & (1 << i)) {
      motor_states |= 1 << i;
    }
  }

  // If we are supposed to dispense something, also turn on the motor
  if (dispensingMotor > 0) {
    
    // If the correct bit in motor_states is already set, that means the switch
    // is pressed already, so the above loop wil take care of dispensing the
    // soda the rest of the way
    if ( !(motor_states & 1 << (dispensingMotor - 1)) ) {
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


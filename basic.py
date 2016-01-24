import itertools
import RPi.GPIO as GPIO
import smbus

import time

# First element of tuple is device that the pin is on:
# Pi is 0
# Bottom arduino is 1
# Top arduino is 2
# Second element is the pin number on that device
motor_switch_pins = [ (1, i) for i in [16, 17, 13, 12, 15, 10, 11] ]
motor_pins = [ (1, i) for i in [2, 3, 8, 9, 4, 5, 6, 7] ]
can_sensor_pins = [ (2, i) for i in [11, 10, 14, 12, 16, 15, 13, 17] ]

# TODO
coin_pin = (0, 4)
selection_pins = [ (0, i) for i in [17, 27, 22, 10, 9, 11, 7, 8] ]

input_pins = list(itertools.chain(motor_switch_pins, can_sensor_pins, coin_pin, selection_pins))
output_pins = motor_pins



# I2C Addresses
arduino_1_addr = 0x1c
arduino_2_addr = 0x1d


bus = smbus.SMBus(1)

def setup_raspi_gpio():
    for pin in input_pins:
        if pin[0] == 0:
            GPIO.setup(pin[1], GPIO.IN)
    for pin in output_pins:
        if pin[0] == 0:
            GPIO.setup(pin[1], GPIO.OUT)

def set_high_pin_code(pin):
    assert pin in xrange(2, 16)
    return pin + 64

def set_low_pin_code(pin):
    assert pin in xrange(2, 16)
    return pin + 64

def read_pin_code(pin):
    assert pin in xrange(2, 16)
    return pin + 64

def read_pin(pin):
    if pin[0] == 0:
        return GPIO.input(pin_to_raw_pin[pin])
    else:
        addr = arduino_1_addr if pin[0] == 1 else arduino_2_addr
        bus.write_byte(addr, read_pin_code(pin[1]))
        time.sleep(.1)
        return bus.read_byte(addr)

def write_pin(pin, state):
    if pin[0] == 0:
        GPIO.output(pin_to_raw_pin[pin], state)
    else:
        addr = arduino_1_addr if pin[0] == 1 else arduino_2_addr
        code = set_high_pin_code(pin[1]) if state \
                                         else set_low_pin_code(pin[1])
        bus.write_byte(addr, code)



def valid_swipe_occured():
    # TODO
    return False



# States:
# Idle / waiting for money/card swipe
# Waiting for selection
# Waiting for motor

wait_for_money, wait_for_selection, wait_for_motor_switch_unpress, \
    wait_for_motor_switch_press = range(4)

def main():
    setup_raspi_gpio()

    state = wait_for_money

    selection = 0

    while True:
        if state == wait_for_money:
            if read_pin(coin_pin) or valid_swipe_occured():
                state = wait_for_selection
        elif state == wait_for_selection:
            selection = get_selection()
            if selection > 0:
                write_pin(motor_pins[selection-1], 1)
                state = wait_for_motor_switch_press
        elif state == wait_for_motor_switch_unpress:
            if not read_pin(motor_switch_pins[selection-1]):
                state = wait_for_motor_switch_press
        elif state == wait_for_motor_switch_press:
            if read_pin(motor_switch_pins[selection-1]):
                state = wait_for_money

def test():
    p = can_sensor_pins[3]
    writeloop()
    
def readloop():
    while True:
        i = input('Pin to read? ')
        print "  value: %d" % read_pin((1, i))

def writeloop():
    while True:
        i = input('Pin to write? ')
        state = 0 != input('Value (0 or 1) to write? ')
        write_pin((1, i), state)

test()

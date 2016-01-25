import itertools
import RPi.GPIO as GPIO
import smbus

import time

motor_arduino_addr = 0x1c
can_sensor_arduino_addr = 0x1d

# TODO
coin_pin = 4
#pins that listen to input buttons
selection_pins = [4, 17, 27, 22, 10, 9, 11]
#chute correspondence: (1,2), 3, 4, 5, 6, 7 8
#so the random button shares two chutes, 1 and 2

bus = smbus.SMBus(1)

def setup_raspi_gpio():
    for pin in itertools.chain(selection_pins, coin_pin):
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def write_pin(pin, state):
    if pin[0] == 0:
        GPIO.output(pin_to_raw_pin[pin], state)
    else:
        addr = arduino_1_addr if pin[0] == 1 else arduino_2_addr
        code set_pin_code(pin[1], state)
        bus.write_byte(addr, code)

def valid_swipe_occured():
    # TODO
    return False

# updates array of fullness
# when we read a byte, we get a binary number
# in which each bit is the fullnesss of a chute
def update_chute_fullness(chute_fullness):
    byte = bus.read_byte(can_sensor_arduino_addr)
    bits = [int(x) for x in bin(byte)]
    chute_fullness[:] = bits(byte)

def get_selection():
    for i, pin in enumerate(selection_pins):
        if not GPIO.input(pin):
            return i+1
    return 0

# States:
# Idle / waiting for money/card swipe
# Waiting for selection
# Waiting for motor

wait_for_money, wait_for_selection = range(2)

def main():
    setup_raspi_gpio()

    state = wait_for_money
    # array that keeps track of which chutes are open (0 means no soda)
    chute_fullness = [0, 0, 0, 0, 0, 0, 0, 0]

    selection = 0

    while True:
        update_chute_fullness(chute_fullness)
        if state == wait_for_money:
            if not GPIO.input(coin_pin) or valid_swipe_occured():
                state = wait_for_selection
        elif state == wait_for_selection:
            selection = get_selection()
            if selection == 1: #user chose random soda
                selection = random.choice(0,1)
            if selection > 0 and chute_fullness[selection]:
                bus.write_byte(motor_arduino_addr, selection)
                state = wait_for_motor_switch_press

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

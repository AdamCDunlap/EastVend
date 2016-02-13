import sys
import itertools
import RPi.GPIO as GPIO
import serial
import random
import time

# TODO
coin_pin = 25
#pins that listen to input buttons
selection_pins = [4, 17, 27, 22, 10, 9, 11]
#chute correspondence: (1,2), 3, 4, 5, 6, 7 8
#so the random button shares two chutes, 1 and 2

ser = serial.Serial('/dev/ttyUSB0', 9600)

def setup_raspi_gpio():
    GPIO.setmode(GPIO.BCM)
    for pin in itertools.chain(selection_pins, [coin_pin]):
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def valid_swipe_occured():
    # TODO
    return False

# updates array of fullness
# when we read a byte, we get a binary number
# in which each bit is the fullnesss of a chute
def get_chute_fullness():
    byte = ser.read()
    bits = [int(x) for x in bin(ord(byte))[2:].zfill(8)]
    return bits

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
    # list that keeps track of which chutes are full (1 means no soda)
    chute_fullness = [0, 0, 0, 0, 0, 0, 0, 0]

    selection = 0

    while True:
        chute_fullness[:] = get_chute_fullness()
        if state == wait_for_money:
            if not GPIO.input(coin_pin) or valid_swipe_occured():
                print 'Got money'
                state = wait_for_selection
        elif state == wait_for_selection:
            selection = get_selection()
            if selection == 1: #user chose random soda
                selection = random.choice([0,0,0,1,1,1,1,2,3,4,5,6,7])
            if selection > 0 and not chute_fullness[selection]:
                print 'Dispensing', selection
                ser.write(chr(selection))
                state = wait_for_money

if __name__ == '__main__':
    main()

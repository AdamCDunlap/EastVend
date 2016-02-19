import sys
import os
import itertools
import RPi.GPIO as GPIO
import serial
import random
import time
import logging


# TODO
coin_pin = 25
#pins that listen to input buttons
selection_pins = [4, 17, 27, 22, 10, 9, 11]
selection_names = ['Random', 'Rootbeer', 'Coke',
                   'Cherry Coke', 'Sprite',
                   'Mountain Dew', 'Canada Dry']
#chute correspondence: (1,2), 3, 4, 5, 6, 7 8
#so the random button shares two chutes, 1 and 2
TIMEOUT = 360 # Seconds


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
got_money_ts = None

def setup_logging():
    eastVendDir = sys.argv[1]

    logDir = '%s/data/log' % eastVendDir
    if not os.path.exists(dataDir):
        os.makedirs(dataDir)

    logging.basicConfig(filename='%s/time-data.log' % logDir,
                        filemode='a',
                        format='%(asctime)s %(message)s',
                        level=logging.DEBUG)

def main():
    setup_raspi_gpio()
    setup_logging()

    state = wait_for_money
    # list that keeps track of which chutes are full (1 means no soda)
    chute_fullness = [0, 0, 0, 0, 0, 0, 0, 0]

    selection = 0

    while True:
        if state == wait_for_money:
            if not GPIO.input(coin_pin) or valid_swipe_occured():
                print 'Got money'
                state = wait_for_selection
                got_money_ts = time.time()
        elif state == wait_for_selection:
            selection = get_selection()
            chute_fullness[:] = get_chute_fullness()
            if selection == 1: #user chose random soda
                selection = random.choice([0,0,0,1,1,1,1,2,3,4,5,6,7])
            elif selection > 0 and not chute_fullness[selection]:
                select_time = time.time() - got_money_ts
                msg = '%s,%.1f' % (selection_names[selection-1], select_time)
                logging.info(msg)
                print 'Dispensing', selection
                ser.write(chr(selection))
                state = wait_for_money
            elif selection = -1 and time.time() > got_money_ts + TIMEOUT:
                print 'Disregarding ``money insertion'' 6 minutes old.'
                state = wait_for_money

if __name__ == '__main__':
    main()

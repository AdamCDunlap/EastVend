import sys
import os
import itertools
import RPi.GPIO as GPIO
import serial
import random
import time
import logging
import Queue
import thread


# TODO
coin_pin = 25
#pins that listen to input buttons
selection_pins = [4, 17, 27, 22, 10, 9, 11]
selection_names = ['Random', 'Rootbeer', 'Coke',
                   'Cherry Coke', 'Sprite',
                   'Mountain Dew', 'Canada Dry']
#chute correspondence: (1,2), 3, 4, 5, 6, 7 8
#so the random button shares two chutes, 1 and 2

RFID_PATH = '/dev/tty'

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
    if not os.path.exists(logDir):
        os.makedirs(logDir)

    logging.basicConfig(filename='%s/time-data.log' % logDir,
                        filemode='a',
                        format='%(asctime)s %(message)s',
                        level=logging.DEBUG)

def mk_populate_queue_fn(queue):
    def listener():
        f = open(RFID_PATH)
        while True:
            raw = f.readline()[2:-3]
            if len(raw) == 8:
                queue.put(int(raw))

def main():
    setup_raspi_gpio()
    setup_logging()

    state = wait_for_money if len(sys.argv) < 3 else wait_for_selection
    got_money_ts = time.time()

    # Set up queue of ID numbers and thread to populate it
    #  Can use `id_queue.empty()` and `id_queue.get()`
    id_queue = Queue.Queue()
    thread.start_new_thread(mk_populate_queue_fn(id_queue))

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
            # If no button has been hit for 5 minutes, cancel
            if time.time() - got_money_ts > 300:
                state = wait_for_money
                msg = 'Timed out'
                logging.info(msg)
            selection = get_selection()
            chute_fullness[:] = get_chute_fullness()
            if selection == 1: #user chose random soda
                selection = random.choice([0,0,0,0,0,1,1,1,1,1,2,3,4,5,6,7])
            if selection > 0 and not chute_fullness[selection]:
                select_time = time.time() - got_money_ts
                msg = '%s,%.1f' % (selection_names[selection-1], select_time)
                logging.info(msg)
                print 'Dispensing', selection
                ser.write(chr(selection))
                state = wait_for_money

if __name__ == '__main__':
    main()

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
import signal


coin_pin = 25
#pins that listen to input buttons
selection_pins = [4, 17, 27, 22, 10, 9, 11]
selection_names = ['Random', 'Coke', 'Root Beer',
                   'Sprite', 'Fanta',
                   'Mountain Dew', 'Canada Dry']
#chute correspondence: (1,2), 3, 4, 5, 6, 7 8
#so the random button shares two chutes, 1 and 2

RFID_PATH = '/dev/tty'

ser = serial.Serial('/dev/ttyUSB0', 9600)

eastVendDir = '/home/pi/EastVend/'

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
    bits.reverse()
    return bits

last_states = [False for _ in selection_pins]
last_rise_times = [time.time() for _ in selection_pins]
def get_selection():
    states = [not GPIO.input(pin) for pin in selection_pins]
    now = time.time()
    for i in range(len(selection_pins)):
        if not last_states[i] and states[i]:
            last_rise_times[i] = now

    last_states[:] = states

    for i,st in enumerate(states):
        if st and now - last_rise_times[i] > .3:
            return i+1

    return 0

# States:
# Idle / waiting for money/card swipe
# Waiting for selection
# Waiting for motor

wait_for_money, wait_for_selection = range(2)
got_money_ts = [None]

def setup_logging():
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
    with open('/tmp/vend.pid', 'w') as f:
        f.write(str(os.getpid()))

    setup_raspi_gpio()
    setup_logging()

    state = [wait_for_money]
    got_money_ts[0] = time.time()

    # Set up queue of ID numbers and thread to populate it
    #  Can use `id_queue.empty()` and `id_queue.get()`
    #id_queue = Queue.Queue()
    #thread.start_new_thread(mk_populate_queue_fn(id_queue))

    # If this process gets a USR1 signal, then pretend money was just inserted
    def pretend_got_money(signal, frame):
        state[0] = wait_for_selection
        got_money_ts[0] = time.time()
        logging.info('Received signal, giving soda')
    signal.signal(signal.SIGUSR1, pretend_got_money)

    # list that keeps track of which chutes are full (1 means no soda)
    chute_fullness = [0, 0, 0, 0, 0, 0, 0, 0]

    selection = 0

    coin_pin_time = time.time()
    coin_pin_last = 1

    while True:
        selection = get_selection()

        coin_pin_now = GPIO.input(coin_pin)
        if coin_pin_now != coin_pin_last:
            now = time.time()
            if (coin_pin_now == 1):
                logging.info("From %s to %s after %s seconds" % (coin_pin_last,
                        coin_pin_now, now - coin_pin_time))
            coin_pin_time = now
            coin_pin_last = coin_pin_now
        if state[0] == wait_for_money:
            if (coin_pin_last == 0) and (time.time() - coin_pin_time > 0.050) or valid_swipe_occured():
                print 'Got money'
                state[0] = wait_for_selection
                got_money_ts[0] = time.time()
        elif state[0] == wait_for_selection:
            # If no button has been hit for 5 minutes, cancel
            if time.time() - got_money_ts[0] > 300:
                state[0] = wait_for_money
                msg = 'Timed out'
                logging.info(msg)

            chute_fullness[:] = get_chute_fullness()

            if selection == 1: #user chose random soda
                selection = random.choice([2,3,4,5,6,7]) if random.random() < .15 else random.choice([0,1])
            if selection > 0:
                chute_fullness[:] = get_chute_fullness()
                logging.info("Chute fullness is " + str(chute_fullness))
                if chute_fullness[selection]:
                    print "Soda %s is all out" % selection_names[selection - 1]
                else:
                    select_time = time.time() - got_money_ts[0]
                    msg = '%s,%.1f' % (selection_names[selection-1], select_time)
                    logging.info(msg)
                    print 'Dispensing', selection
                    ser.write(chr(selection))
                    state[0] = wait_for_money

if __name__ == '__main__':
    main()

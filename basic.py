import sys

import itertools
import RPi.GPIO as GPIO
import smbus

import time

motor_arduino_addr = 0x1c
can_sensor_arduino_addr = 0x19

# TODO
coin_pin = 25
#pins that listen to input buttons
selection_pins = [4, 17, 27, 22, 10, 9, 11]
#chute correspondence: (1,2), 3, 4, 5, 6, 7 8
#so the random button shares two chutes, 1 and 2

bus = smbus.SMBus(1)

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
    #byte = bus.read_byte(can_sensor_arduino_addr)
    byte = 0xff
    bits = [int(x) for x in bin(byte)[2:]]
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
    # array that keeps track of which chutes are open (0 means no soda)
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
            if selection > 0 and chute_fullness[selection]:
                print 'Dispensing', selection
                bus.write_byte(motor_arduino_addr, selection)
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

#test()

def testMtr():
    for i in [4, 5, 6, 7, 2, 3]:
        print 'Trying to dispense soda %d' % i
        bus.write_byte(motor_arduino_addr, i)
        time.sleep(5)
# for i in xrange(int(sys.argv[2])):
#     bus.write_byte(motor_arduino_addr, int(sys.argv[1]))
#     time.sleep(5)
# 
print bus.write_byte(motor_arduino_addr, int(sys.argv[1]))

#bus.write_byte(motor_arduino_addr, 0)

#setup_raspi_gpio()

#bus.write_byte(motor_arduino_addr, 1)
#time.sleep(.1)
#while True:
#    print bus.read_byte(can_sensor_arduino_addr)
#    time.sleep(.1)
#    #print bus.read_byte(motor_arduino_addr)
#    #time.sleep(.1)
# main()
#while True:
#    #time.sleep(.2)
#    try:
#        print '\n', bus.write_byte(motor_arduino_addr, 3)#can_sensor_arduino_addr)
#        break
#    except:
#        print '.',

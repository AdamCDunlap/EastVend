#!/usr/bin/python
import struct
import time
import sys
import signal
import os

infile_path = '/dev/input/by-id/usb-c216_0101-event-kbd'

data_path = "/home/pi/EastVend/data"

#long int, long int, unsigned short, unsigned short, unsigned int
FORMAT = 'llHHI'
EVENT_SIZE = struct.calcsize(FORMAT)

#open file in binary mode

QUESTION_MARK = 53
NEWLINE = 28
SEMICOLON = 39

def code_to_number(code):
    if code == 11:
        return '0'
    elif code >= 2 and code <= 10:
        return str(code - 1)
    else:
        return None

def process(numlist):
    if len(numlist) == 10:
        id_num_str = ''.join(numlist[1:-1])
        del numlist[:]
        return try_charge(id_num_str)
    else:
        del numlist[:]
        return False

def log(msg):
    with open(data_path + "/log/card-swipe.log", "a") as f:
        f.write("[%s]: %s\n" % (time.asctime(time.localtime()), msg))

def try_charge(id_num_str):
    log("Id {%s} tried to swipe" % id_num_str)
    users_dir = data_path + "/users/"
    if id_num_str in os.listdir(users_dir):
        data = None
        with open(users_dir + id_num_str, "r") as f:
            data = f.readline().split("\000")
        data[1] = str(int(data[1]) + 1)
        with open(users_dir + id_num_str, "w") as f:
            f.write('\000'.join(data))
        return True
    else:
        return False

def main():
    with open('/tmp/read-card.pid', 'w') as f:
        f.write(str(os.getpid()))
    in_file = open(infile_path, "rb")
    event = in_file.read(EVENT_SIZE)

    l = []
    while event:
        (tv_sec, tv_usec, type, code, value) = struct.unpack(FORMAT, event)

        if value == 1:
            number = code_to_number(code)
            if code == NEWLINE:
                give_them_soda = process(l)
                if give_them_soda:
                    log('Giving soda')
                    with open('/tmp/vend.pid', 'r') as pidf:
                        os.kill(int(pidf.read()), signal.SIGUSR1)
            if number is not None:
                l.append(number)


        #if type != 0 or code != 0 or value != 0:
        #    print("Event type %u, code %u, value %u at %d.%d" % \
        #        (type, code, value, tv_sec, tv_usec))
        #else:
        #    # Events with code, type and value == 0 are "separator" events
        #    print("===========================================")

        event = in_file.read(EVENT_SIZE)

    in_file.close()

def sendmail(msg, to):
    pass

if __name__ == '__main__':
    main()

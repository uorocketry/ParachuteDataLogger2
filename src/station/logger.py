import serial
import time
from time import sleep
import os
import re
from threading import Thread
class Command:
    PING = bytes([1])
    READ_SINGLE = bytes([2])
    START_LOGGING = bytes([3])
    STOP_LOGGING = bytes([4])

class Reading:
    def __init__(self, x, y, z, direction, speed):
        self.x = x
        self.y = y
        self.z = z
        self.direction = direction
        self.speed = speed
    
    def __str__(self):
        return 'X:{0} Y:{1} Z:{2} Dir:{3} Speed:{4}'.format(self.x, self.y, self.z, self.direction, self.speed)

ser = serial.Serial()

def get_serial_ports():
    ports = []
    for port_num in range(256):
        try:
            port = str(port_num)
            s = serial.Serial('COM' + port)
            s.close()
            ports.append(port)
        except (OSError, serial.SerialException):
            pass
    return ports

def get_input():
    while True:
        result = input('Enter command:\n0: Ping\n1: Single Reading\n2: Start Logging\n3: Stop Logging\n4: Exit\n').strip()
        if result == '0':
            if ping():
                print('Reply recieved from loadcell board')
        elif result == '1':
            read_single()
        elif result == '2':
            start_logging()
        elif result == '3':
            stop_logging()
        elif result == '4':
            return False # Exit
        else:
            continue # Invalid input, Continue get_input loop
        return True # Keep looping

def ask_yes_no(question):
    while True:
        response = input('{} (Y/N)\n'.format(question)).strip().capitalize()
        if response == 'Y':
            return True
        elif response == 'N':
            return False

def open_log_file():
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
        print('Created log directory {}'.format(log_dir))

    while True:
        log_file = input('Enter file name\n').strip()
        if re.match('^[\\w\\-. ]+$', log_file) == None:
            print('Invalid file name')
            continue

        log_path = os.path.join(log_dir, log_file + '.csv')
        if os.path.isfile(log_path) and not ask_yes_no('File already exists. Overwrite?'):
            continue

        try:
            log = open(log_path, 'w')
            log.close()
        except Exception as e:
            print('Error opening log file for writing: {}'.format(e))
            continue

        print('Log will be saved as {}'.format(log_path))
        return log_path

def ping():
    start_time = time.time()
    ser.write(Command.PING)
    while(True):
        if ser.inWaiting() > 0:
            if ser.read(1) == Command.PING:
                while ser.inWaiting() > 0:
                    ser.read() # Flush buffer
                return True
        elif time.time() - start_time > 2:
            print('Request timed out')
            return False

def sensors_ready():
    return ser.inWaiting() >= 16

def read_sensors():
    return Reading(
        int.from_bytes(ser.read(4), byteorder='little', signed=True),
        int.from_bytes(ser.read(4), byteorder='little', signed=True),
        int.from_bytes(ser.read(4), byteorder='little', signed=True),
        int.from_bytes(ser.read(2), byteorder='little', signed=True),
        int.from_bytes(ser.read(2), byteorder='little', signed=True))

def read_single():
    start_time = time.time()
    ser.write(Command.READ_SINGLE)
    while(True):
        if sensors_ready():
            print(read_sensors())
            return True
        elif time.time() - start_time > 2:
            print('Request timed out')
            return False

stop_read = True
logging_thread = Thread()
def read_continuous(log_path):
    global stop_read
    stop_read = False
    log_file = open(log_path, 'w')

    start_time = time.time()
    latest_time = start_time

    ser.write(Command.START_LOGGING)
    while(True):
        if sensors_ready():
            reading = read_sensors()
            log_file.write('{}, {}, {}, {}\n'.format(round(time.time() - start_time, 6), reading.x, reading.y, reading.z))
            latest_time = time.time()

        elif time.time() - latest_time > 2:
            print('Connection timed out')
            log_file.close()
            stop_read = True
            return False
        elif stop_read:
            ser.write(Command.STOP_LOGGING)
            # TODO: Add stop comfirmation/flush recieve buffer
            log_file.close()
            print('Logging stopped')
            return True

def start_logging():
    # TODO: Don't start logging if already logging
    log_path = open_log_file()
    global logging_thread
    logging_thread = Thread(target=read_continuous, args=(log_path,))
    logging_thread.start()

def stop_logging():
    global stop_read
    if not stop_read:
        stop_read = True
        logging_thread.join()
    else:
        print('Not currently logging')

if __name__ == '__main__':
    availablePorts = get_serial_ports()
    selectedPort = ''
    if len(availablePorts) == 0:
        print('No availible serial ports')
        raise SystemExit
    elif len(availablePorts) == 1:
        selectedPort = availablePorts[0]
    else:
        while True:
            selectedPort = input('Select an availible port: {}\n'.format(', '.join(availablePorts)))
            if selectedPort in availablePorts:
                break

    ser = serial.Serial('COM{}'.format(selectedPort), 115200, timeout=0, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
    print('Connected to COM{}'.format(selectedPort))
    print('Waiting to connect...')
    sleep(2)
    print('Checking board connections...')
    if ping():
        print('Connections OK')
    else:
        print('Check board connections and try again')
        raise SystemExit

    while get_input():
        continue

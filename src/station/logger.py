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
    def __init__(self, x, y, z, direction, speed, time=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.direction = direction
        self.speed = speed
        self.time = time

    def __add__(self, other):
        return Reading(self.x + other.x, self.y + other.y, self.z + other.z, 
            self.direction + other.direction, self.speed + other.speed, self.time)

    def __sub__(self, other):
        return Reading(self.x - other.x, self.y - other.y, self.z - other.z, 
            self.direction - other.direction, self.speed - other.speed, self.time)

    def __mul__(self, other):
        return Reading(self.x*other.x, self.y*other.y, self.z*other.z, 
            self.direction*other.direction, self.speed*other.speed, self.time)

    def scale(self, coeff):
        return Reading(self.x*coeff, self.y*coeff, self.z*coeff, 
            self.direction*coeff, self.speed*coeff, self.time)

    def __str__(self):
        return 'Time:{} X:{} Y:{} Z:{} Dir:{} Speed:{}'.format(
            '{:.3f}'.format(self.time).ljust(8), 
            '{:.2f}'.format(self.x).ljust(8), 
            '{:.2f}'.format(self.y).ljust(8), 
            '{:.2f}'.format(self.z).ljust(8), 
            '{:.0f}'.format(self.direction).ljust(6), 
            '{:.1f}'.format(self.speed).ljust(6))

    def csv_line(self):
        return '{:.3f}, {:.2f}, {:.2f}, {:.2f}, {:.1f}, {:.1f}\n'.format(
            self.time, self.x, self.y, self.z, 
            self.direction, self.speed)

scale = Reading(x=0.000168354, y=0.0000781784, z=0.0000786995, direction=0.452261, speed=0.0243137)
offset = Reading(x=0, y=0, z=0, direction=-90, speed=-4.9)
ser = serial.Serial()
OFFSET_FILE = 'offsets.csv'

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

def ask_yes_no(question):
    while True:
        response = input('{} (Y/N)\n'.format(question)).strip().capitalize()
        if response == 'Y':
            return True
        elif response == 'N':
            return False

def ask_int(question, min_val, max_val, default_val):
    while True:
        response = input('{} (min:{} max:{} default:{})\n'.format(question, min_val, max_val, default_val)).strip()
        if response.isdigit():
            response_int = int(response)
            if response_int >= min_val and response_int <= max_val:
                return response_int
        elif response == '':
            return default_val

def get_input():
    while True:
        result = input('Enter command:\n0: Ping\n1: Single Reading\n2: Average Reading\n3: Tare\n4: Start Logging\n5: Exit\n').strip()
        if result == '0':
            if ping():
                print('Reply recieved from loadcell board')
        elif result == '1':
            read_single()
        elif result == '2':
            read_average(ask_int('Enter number of samples', 2, 2000, 20))
        elif result == '3':
            tare(ask_int('Enter number of samples', 2, 2000, 40))
        elif result == '4':
            start_logging()
            input()
            stop_logging()
        elif result == '5':
            return False # Exit
        else:
            continue # Invalid input, Continue get_input loop
        return True # Keep looping

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

def sensor_data_ready():
    return ser.inWaiting() >= 16

def read_sensors(raw=False):
    raw_reading = Reading(
        int.from_bytes(ser.read(4), byteorder='little', signed=True),
        int.from_bytes(ser.read(4), byteorder='little', signed=True),
        int.from_bytes(ser.read(4), byteorder='little', signed=True),
        int.from_bytes(ser.read(2), byteorder='little', signed=True),
        int.from_bytes(ser.read(2), byteorder='little', signed=True))
    if raw:
        return raw_reading
    return raw_reading*scale + offset

def read_single():
    start_time = time.time()
    ser.write(Command.READ_SINGLE)
    while(True):
        if sensor_data_ready():
            print(read_sensors())
            return True
        elif time.time() - start_time > 2:
            print('Request timed out')
            return False

def read_average(samples):
    latest_time = time.time()
    ser.write(Command.START_LOGGING)
    total = Reading(0, 0, 0, 0, 0)
    i = 0
    while i < samples:
        if sensor_data_ready():
            i += 1
            total += read_sensors()
            average = total.scale(1/i)
            print(average, '{0}/{1}'.format(i, samples), end='\r')
            latest_time = time.time()

        elif time.time() - latest_time > 2:
            print('Connection timed out')
            return (False, None)
    ser.write(Command.STOP_LOGGING)
    print()
    return (True, average)

def tare(samples):
    reading = read_average(samples)
    if reading[0]:
        offset.x -= reading[1].x
        offset.y -= reading[1].y
        offset.z -= reading[1].z
        print('Scale offsets set to: x={} y={} z={}'.format(offset.x, offset.y, offset.z))
        try:
            with open(OFFSET_FILE, 'w') as f:
                f.write('{}, {}, {}'.format(offset.x, offset.y, offset.z))
        except Exception as ex:
            print('Failed to save scale offsets with error {}'.format(ex))

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
        if sensor_data_ready():
            reading = read_sensors()
            reading.time = round(time.time() - start_time, 6)
            log_file.write(reading.csv_line())
            print(reading, end='\r')
            latest_time = time.time()

        elif time.time() - latest_time > 2:
            print('Connection timed out')
            log_file.close()
            stop_read = True
            print()
            return False
        elif stop_read:
            ser.write(Command.STOP_LOGGING)
            # TODO: Add stop comfirmation/flush recieve buffer
            log_file.close()
            print('\nLogging stopped')
            return True

def start_logging():
    # TODO: Don't start logging if already logging
    log_path = open_log_file()
    global logging_thread
    print('Press enter to stop logging')
    logging_thread = Thread(target=read_continuous, args=(log_path,))
    logging_thread.start()

def stop_logging():
    global stop_read
    if not stop_read:
        stop_read = True
        logging_thread.join()
    else:
        print('Not currently logging')

def load_offsets():
    if os.path.exists(OFFSET_FILE):
        try:
            with open(OFFSET_FILE, 'r') as f:
                values = f.read().split(',')
                offset.x = float(values[0])
                offset.y = float(values[1])
                offset.z = float(values[2])
                print('Scale offsets loaded as: x={} y={} z={}'.format(offset.x, offset.y, offset.z))
                return
        except Exception as ex:
            print('Failed to load scale offsets with error {}'.format(ex))
    else:
        print('Scale offset file {} not found'.format(OFFSET_FILE))
    print('Using default scale offsets: x={} y={} z={}'.format(offset.x, offset.y, offset.z))

if __name__ == '__main__':
    load_offsets()

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

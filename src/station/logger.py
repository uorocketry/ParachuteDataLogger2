import serial
import time
from time import sleep

class Command:
    PING = bytes([1])
    READ_SINGLE = bytes([2])
    START_LOGGING = bytes([3])
    STOP_LOGGING = bytes([4])

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
            continue # Invalid input, Continue
        return True # Keep looping

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

def read_single():
    start_time = time.time()
    ser.write(Command.READ_SINGLE)
    while(True):
        if ser.inWaiting() >= 12:
            x = int.from_bytes(ser.read(4), byteorder='little', signed=True)
            y = int.from_bytes(ser.read(4), byteorder='little', signed=True)
            z = int.from_bytes(ser.read(4), byteorder='little', signed=True)
            print(x)
            print(y)
            print(z)
            return True
        elif time.time() - start_time > 2:
            print('Request timed out')
            return False

def start_logging():
    print('Command not implemented')

def stop_logging():
    print('Command not implemented')

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

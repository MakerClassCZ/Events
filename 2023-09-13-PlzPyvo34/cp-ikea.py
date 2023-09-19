import os
import time
import board
import busio
import microcontroller

uart = busio.UART(tx=board.GP4, rx=board.GP5, baudrate=9600)

measurements = [0, 0, 0, 0, 0]
measurement_idx = 0

def valid_header(d):
    headerValid = (d[0] == 0x16 and d[1] == 0x11 and d[2] == 0x0B)
    return headerValid

while True:
    try:
        data = uart.read(32)  # read up to 32 bytes
        #print(data)  # this is a bytearray type
        #time.sleep(0.01)
        if data is not None:
            v = valid_header(data)
            if v is True:
                measurement_idx = 0
                start_read = True
            if start_read is True:
                pm25 = (data[5] << 8) | data[6]
                measurements[measurement_idx] = pm25
                if measurement_idx == 4:
                    start_read = False
                measurement_idx = (measurement_idx + 1) % 5
                print(pm25)
                #print(measurements)
    except Exception as e: # pylint: disable=broad-except
        print("Error:\n", str(e))
        time.sleep(10)
        microcontroller.reset()
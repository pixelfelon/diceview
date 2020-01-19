import serial
import time
ser = serial.Serial('/dev/ttyACM0', 115200)
time.sleep(0.1)
ser.write('s0\r\n'.encode())
ser.flush()
time.sleep(0.5)
ser.write('s0\r\n'.encode())
ser.flush()
time.sleep(1)
ser.write('s170\r\n'.encode())
ser.flush()
ser.close()


###############################################################################
# Project: Polyhedral Dice Statistical Analysis (Diceview)
# File   : motion.py
#
# Control dice shaker actuator.
#
# Copyright (c) 2020 Diceview Team
# Released under the MIT License.
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20200117       Created                                        jrowley
#
###############################################################################

import time
import serial

class Motion(object):
	def __init__(self):
		# Set up connection to controller.
		self.ser = None
		try:
			self.ser = serial.Serial('/dev/ttyACM0', 115200)
			time.sleep(0.1)
			self.ser.write('s170\r\n'.encode())
			self.ser.flush()
		except serial.serialutil.SerialException:
			self.ser = None
			print("Couldn't open serial comms to servo controller!")
	
	def roll(self):
		# Block until dice roll actuation is complete.
		if self.ser is not None:
			time.sleep(0.5)
			self.ser.write('s0\r\n'.encode())
			self.ser.flush()
			time.sleep(1)
			self.ser.write('s170\r\n'.encode())
			self.ser.flush()
			time.sleep(1)
		else:
			time.sleep(0.5)
	
	def __del__(self):
		if self.ser is not None:
			self.ser.close()

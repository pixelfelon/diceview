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

class Motion(object):
	def __init__(self):
		# Set up PWM or whatever for the servo.
		pass
	
	def roll(self):
		# Block until dice roll actuation is complete.
		time.sleep(0.1)

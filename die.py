###############################################################################
# Project: Polyhedral Dice Statistical Analysis (Diceview)
# File   : die.py
#
# Data for a single die.
#
# Copyright (c) 2020 Diceview Team
# Released under the MIT License.
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20200117       Created                                        jrowley
#
###############################################################################

import numpy as np

class Die(object):
	def __init__(self, name, sides):
		self.name = name
		self.sides = sides
		self.count = np.zeros(self.sides)
	
	def chisquared(self):
		# should calculated the chi squared of the count array
		return 0.0

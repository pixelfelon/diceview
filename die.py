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
from scipy import stats


class Die(object):
	def __init__(self, name, sides):
		self.name = name
		self.sides = sides
		self.count = np.zeros(self.sides)
	
	def add_roll(self, roll):
		self.count[roll - 1] += 1
	
	def average(self):
		rollsum = 0
		for side in range(self.sides):
			rollsum += (side + 1) * self.count[side]
		return rollsum / np.sum(self.count)
	
	def rolls(self):
		return int(np.sum(self.count))
	
	def chi_squared(self):
		# should calculated the chi squared of the count array
		return stats.chisquare(self.count)[0]

###############################################################################
# Project: Polyhedral Dice Statistical Analysis (Diceview)
# File   : graphs.py
#
# Plot dice data with Seaborn.
#
# Copyright (c) 2020 Diceview Team
# Released under the MIT License.
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20200117       Created                                        jrowley
#
###############################################################################

def count_graph(die):
	# Return a plot object which is a bar graph of how many times each face was rolled, autoscaled to the min/max of
	# the data + 10% on either side.
	# Parameter die is a Die object from die.py.
	pass

def chi_graph(*args, last = None):
	# Return two values:
	#	A plot object which is a multi-trace line graph of chi-squared over time for the dice.
	#	A vaguely-defined object of historical data which should be passed in as the "last" parameter to future calls.
	# Pass in as many Die objects as desired.
	pass

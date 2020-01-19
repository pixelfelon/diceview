###############################################################################
# Project: Polyhedral Dice Statistical Analysis (Diceview)
# File   : graphs.py
#
# Plot dice data with Matplotlib.
#
# Copyright (c) 2020 Diceview Team
# Released under the MIT License.
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20200117       Created                                        jrowley
#
###############################################################################

from matplotlib.figure import Figure
import matplotlib.ticker as tick
import numpy as np


def count_graph(die):
	# Return a plot object which is a bar graph of how many times each face was rolled, autoscaled to the min/max of
	# the data + 10% on either side.
	# Parameter die is a Die object from die.py.
	fig = Figure()
	graph = fig.add_subplot(111)
	fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
	
	graph.bar(range(die.sides), die.count)
	graph.set_xticks(range(die.sides))
	graph.xaxis.set_major_formatter(tick.FuncFormatter(lambda x, y: "{:d}".format(int(x + 1))))
	
	maxc = np.max(die.count)
	minc = np.min(die.count)
	rangec = maxc - minc
	maxc += rangec / 5
	minc -= rangec / 5
	maxc = np.max([maxc, 10])
	minc = np.max([minc, 0])
	graph.set_ylim([minc, maxc])
	
	graph.set_title("Dice Roll Count per Face")
	graph.set_ylabel("Rolls")
	graph.set_xlabel("Face")
	
	return fig


def chi_graph(chi_values):
	# Returns a plot object which is a line graph of chi-squared over time for the dice.
	fig = Figure()
	graph = fig.add_subplot(111)
	fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
	
	graph.plot(range(len(chi_values)), chi_values)
	graph.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
	graph.set_ylim([0, np.max(chi_values) * 1.25])
	
	graph.set_title("Chi-Squared of Roll Frequency over Time")
	graph.set_ylabel("Chi-Squared")
	graph.set_xlabel("Time")
	
	return fig

###############################################################################
# Project: Polyhedral Dice Statistical Analysis (Diceview)
# File   : vision.py
#
# Machine vision for extracting dice values from an image.
#
# Copyright (c) 2020 Diceview Team
# Released under the MIT License.
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20200117       Created                                        jrowley
#
###############################################################################

def process_image(image):
	# Process an opencv image to find dice.
	# Will return two values:
	#	a list of tuples representing dice.
	#		the first element of tuple will be some identifier, i.e. number of sides or color.
	#		the second element will be the number rolled. THIS FUNCTION SHOULD INVERT IT FROM THE BOTTOM VIEW
	#	a version of the source image with additional cool markup.
	return ([(0, 0)], image)

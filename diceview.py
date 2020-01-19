###############################################################################
# Project: Polyhedral Dice Statistical Analysis (Diceview)
# File   : diceview.py
#
# Main script and GUI.
#
# Copyright (c) 2020 Diceview Team
# Released under the MIT License.
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20200117       Derived from SkynetMIA                         jrowley
#
###############################################################################

import math
import os
import time
from enum import Enum

import tkinter
from tkinter import W, E, N, S
import cv2
from PIL import Image, ImageTk
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from vision import VisionThread
from die import Die
import graphs


def clamp_aspect(ratio, width, height):
	width = float(width)
	height = float(height)
	if width > height * ratio:
		width = height * ratio
	elif height > width / ratio:
		height = width / ratio
	width = int(math.ceil(width))
	height = int(math.ceil(height))
	return width, height


class DiceviewApp:
	class States(Enum):
		SAMPLE = 0
		SAMPLE_WAIT = 1
		SAMPLE_READY = 2
	
	PADDING = 5
	ROWMIN = 150
	COLMIN = 500
	
	def __init__(self):
		self.root = tkinter.Tk()
		self.root.title("diceview")
		try:
			self.root.state("zoomed")
		except (tkinter.TclError):

			pass

			m = self.root.maxsize()

			self.root.geometry('{}x{}+0+0'.format(*m))
		self.root.focus_set()
		
		self.root.configure(bg="#ddd", padx=self.PADDING, pady=self.PADDING)
		self.root.rowconfigure(0, minsize=self.ROWMIN, weight=1)
		self.root.rowconfigure(1, minsize=self.ROWMIN, weight=1)
		self.root.rowconfigure(2, minsize=self.ROWMIN, weight=1)
		self.root.rowconfigure(3, minsize=self.ROWMIN, weight=1)
		self.root.columnconfigure(0, minsize=self.COLMIN, weight=2)
		self.root.columnconfigure(1, minsize=self.COLMIN, weight=1)
		self.root.minsize(self.PADDING * 6 + self.COLMIN * 2, self.PADDING * 10 + self.ROWMIN * 4)
		
		self._nullfig = Figure()
		self.graph1 = FigureCanvasTkAgg(self._nullfig, master=self.root)
		self.graph2 = FigureCanvasTkAgg(self._nullfig, master=self.root)
		self.graph3 = FigureCanvasTkAgg(self._nullfig, master=self.root)
		self.graph4 = FigureCanvasTkAgg(self._nullfig, master=self.root)
		self.graph_chi = FigureCanvasTkAgg(self._nullfig, master=self.root)
		self.graph1.get_tk_widget().grid(row=0, column=0, sticky=W + E + N + S, padx=self.PADDING, pady=self.PADDING)
		self.graph2.get_tk_widget().grid(row=1, column=0, sticky=W + E + N + S, padx=self.PADDING, pady=self.PADDING)
		self.graph3.get_tk_widget().grid(row=2, column=0, sticky=W + E + N + S, padx=self.PADDING, pady=self.PADDING)
		self.graph4.get_tk_widget().grid(row=3, column=0, sticky=W + E + N + S, padx=self.PADDING, pady=self.PADDING)
		self.graph_chi.get_tk_widget().grid(
			row=0, column=1, rowspan=2, sticky=W + E + N + S, padx=self.PADDING, pady=self.PADDING)
		
		self.infoframe = tkinter.Frame(self.root, bg="#eee")
		self.infoframe.grid(row=2, column=1, rowspan=2, sticky=W + E + N + S, padx=self.PADDING, pady=self.PADDING)
		self.infoframe.pack_propagate(False)
		
		self.statframe = tkinter.Frame(self.infoframe, bg="#eee", width=200)
		self.statframe.pack(fill=tkinter.Y, padx=10, side=tkinter.LEFT)
		self.statframe.pack_propagate(False)
		
		self.tkimage = tkinter.Label(self.infoframe, bd=0, bg='#eee')
		self.tkimage.pack(fill="both", expand=True)
		self.tkimage.pack_propagate(False)
		
		self.vision = VisionThread()
		self.vision.start()
		
		self.state = self.States.SAMPLE
		self.root.after(1, self.tick)
	
	def tick(self):
		if self.state == self.States.SAMPLE:
			self.vision.sample()
			self.state = self.States.SAMPLE_WAIT
		if self.state == self.States.SAMPLE_WAIT:
			with self.vision.reslock:
				if self.vision.fresh:
					self.state = self.States.SAMPLE_READY
		if self.state == self.States.SAMPLE_READY:
			dice, frame = self.vision.wait_results()
			self.show_frame(frame)
			self.update_stats(dice)
			self.state = self.States.SAMPLE
		
		self.root.after(10, self.tick)
	
	def show_frame(self, frame):
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
		size = clamp_aspect(16.0 / 9.0, self.tkimage.winfo_width(), self.tkimage.winfo_height())
		frame = cv2.resize(frame, size)
		frame = Image.fromarray(frame)
		frame = ImageTk.PhotoImage(frame)
		self.tkimage.configure(image=frame)
		self.tkimage.image = frame
	
	def update_stats(self, dice):
		pass
	
	def shutdown(self):
		self.root.destroy()
		self.vision.stop()
		self.vision.join(timeout=10)
		exit(0)
	
	def run(self):
		self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
		self.root.mainloop()


if __name__ == "__main__":
	app = DiceviewApp()
	app.run()

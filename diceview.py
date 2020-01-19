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


def resize_to_height(img, height):
	ratio = float(height) / float(img.shape[0])
	width = int(math.ceil(float(img.shape[1]) * ratio))
	return cv2.resize(img, (width, height))


def centered_clamp_width(img, width):
	offset = img.shape[1] - width
	if not offset > 0:
		return img
	offset_a = offset // 2
	offset_b = offset_a
	if offset % 2:
		offset_b += 1
	return img[:, offset_a:(img.shape[1] - offset_b)]


class DiceviewApp:
	class States(Enum):
		SAMPLE = 0
		SAMPLE_WAIT = 1
		SAMPLE_READY = 2
	
	def __init__(self):
		self.root = tkinter.Tk()
		self.root.title("diceview")
		self.root.state("zoomed")
		self.root.focus_set()
		
		self.root.configure(bg="#ddd")
		self.root.rowconfigure(0, minsize = 100, weight = 1)
		self.root.rowconfigure(1, minsize = 100, weight = 1)
		self.root.rowconfigure(2, minsize = 100, weight = 1)
		self.root.rowconfigure(3, minsize = 100, weight = 1)
		self.root.columnconfigure(0, minsize = 200, weight = 2)
		self.root.columnconfigure(1, minsize = 200, weight = 1)
		self.root.grid_propagate(False)
		
		self._nullfig = Figure()
		self.graph1 = FigureCanvasTkAgg(self._nullfig, master=self.root)
		self.graph2 = FigureCanvasTkAgg(self._nullfig, master=self.root)
		self.graph3 = FigureCanvasTkAgg(self._nullfig, master=self.root)
		self.graph4 = FigureCanvasTkAgg(self._nullfig, master=self.root)
		self.graph_chi = FigureCanvasTkAgg(self._nullfig, master=self.root)
		self.graph1.get_tk_widget().grid(row = 0, column = 0, sticky=W+E+N+S, padx=5, pady=5)
		self.graph2.get_tk_widget().grid(row = 1, column = 0, sticky=W+E+N+S, padx=5, pady=5)
		self.graph3.get_tk_widget().grid(row = 2, column = 0, sticky=W+E+N+S, padx=5, pady=5)
		self.graph4.get_tk_widget().grid(row = 3, column = 0, sticky=W+E+N+S, padx=5, pady=5)
		self.graph_chi.get_tk_widget().grid(row = 0, column = 1, rowspan = 2, sticky=W+E+N+S, padx=5, pady=5)
		
		self.infoframe = tkinter.Frame(self.root, bg="#000")
		self.infoframe.grid(row = 2, column = 1, rowspan = 2, sticky=W+E+N+S, padx=5, pady=5)
		self.infoframe.grid_propagate(False)
		
		self.statframe = tkinter.Frame(self.infoframe, bg="#eee", width=200)
		self.statframe.pack(fill=tkinter.Y, padx=10, side=tkinter.LEFT)
		
		self.vframe = tkinter.Label(self.infoframe, bd=0, bg='#222')
		self.vframe.pack(fill="both", expand = True)
		self.vframe.grid_propagate(False)
		
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
			if not self.state == self.States.SAMPLE_READY:
				with self.vision.conlock:
					if not self.vision._sample:
						self.state = self.States.SAMPLE
						print("VisionThread forgot to sample!")
		if self.state == self.States.SAMPLE_READY:
			dice, frame = self.vision.wait_results()
			self.show_frame(frame)
			self.update_stats(dice)
			self.state = self.States.SAMPLE
		
		self.root.after(10, self.tick)
	
	def show_frame(self, frame):
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
		size = clamp_aspect(16.0 / 9.0, self.vframe.winfo_width(), self.vframe.winfo_height())
		frame = cv2.resize(frame, size)
		frame = Image.fromarray(frame)
		frame = ImageTk.PhotoImage(frame)
		self.vframe.configure(image=frame)
		self.vframe.image = frame
	
	def update_stats(self, dice):
		pass
	
	def shutdown(self):
		self.root.destroy()
		self.vision.stop()
		self.vision.join(timeout = 10)
		exit(0)
	
	def run(self):
		self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
		self.root.mainloop()


if __name__ == "__main__":
	app = DiceviewApp()
	app.run()

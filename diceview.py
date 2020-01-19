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
from enum import Enum

import tkinter
from tkinter import font
from tkinter import W, E, N, S
import cv2
from PIL import Image, ImageTk
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
	ROWMIN = 400
	COLMIN = 800
	
	FACES = 20
	
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
		self.root.columnconfigure(0, minsize=self.COLMIN, weight=1)
		self.root.columnconfigure(1, minsize=self.COLMIN, weight=1)
		self.root.minsize(self.PADDING * 6 + self.COLMIN * 2, self.PADDING * 6 + self.ROWMIN * 2)
		
		self.graph_bar = tkinter.Frame(self.root)
		self.graph_chi = tkinter.Frame(self.root, bg='#000')
		self.graph_bar.grid(row=0, column=0, sticky=W + E + N + S, padx=self.PADDING, pady=self.PADDING)
		self.graph_chi.grid(row=0, column=1, sticky=W + E + N + S, padx=self.PADDING, pady=self.PADDING)
		self.graph_bar.pack_propagate(False)
		self.graph_chi.pack_propagate(False)
		self._nullfig = Figure()
		self.canvas_bar = FigureCanvasTkAgg(self._nullfig, master=self.graph_bar)
		self.canvas_chi = FigureCanvasTkAgg(self._nullfig, master=self.graph_chi)
		self.canvas_bar.get_tk_widget().pack(fill="both", expand=True)
		self.canvas_chi.get_tk_widget().pack(fill="both", expand=True)
		
		self.imframe = tkinter.Frame(self.root, bg="#eee")
		self.imframe.grid(row=1, column=1, sticky=W + E + N + S, padx=self.PADDING, pady=self.PADDING)
		self.imframe.pack_propagate(False)
		
		self.tkimage = tkinter.Label(self.imframe, bd=0, bg='#eee')
		self.tkimage.pack(fill="both", expand=True)
		
		self.statframe = tkinter.Frame(self.root, bg="#eee")
		self.statframe.grid(row=1, column=0, sticky=W + E + N + S, padx=self.PADDING, pady=self.PADDING)
		self.statframe.rowconfigure(0, weight=1)
		self.statframe.rowconfigure(1, weight=1)
		self.statframe.columnconfigure(0, weight=1)
		self.statframe.columnconfigure(1, weight=1)
		
		self.lilfont = font.Font(family='Trebuchet MS', size=25, weight='normal')
		self.bigfont = font.Font(family='Trebuchet MS', size=75, weight='bold')
		
		positions = {
			"Actuations": (0, 0),
			"Dice Rolls": (0, 1),
			"Average Roll": (1, 0),
			"Chi-Squared": (1, 1)
		}
		self.sf_subs = {}
		self.sf_labels = {}
		self.sf_vars = {}
		for pos in positions:
			self.sf_subs[pos] = tkinter.Frame(self.statframe, bg='#eee')
			self.sf_subs[pos].grid(
				row=positions[pos][0], column=positions[pos][1], sticky=W + E + N + S, padx=30, pady=30)
			self.sf_subs[pos].rowconfigure(0, weight=1)
			self.sf_subs[pos].rowconfigure(1, weight=5)
			self.sf_subs[pos].columnconfigure(0, weight=1)
			self.sf_subs[pos].grid_propagate(False)
			self.sf_labels[pos] = tkinter.Label(self.sf_subs[pos], text=pos, font=self.lilfont, bg='#eee')
			self.sf_labels[pos].grid(row=0, column=0, sticky=W + E)
			self.sf_labels[pos].grid_propagate(False)
			self.sf_vars[pos] = tkinter.Label(self.sf_subs[pos], text="0", font=self.bigfont, bg='#eee')
			self.sf_vars[pos].grid(row=1, column=0, sticky=W + E)
			self.sf_vars[pos].grid_propagate(False)
		
		self.actuations = 0
		self.chi_history = []
		self.die = Die("D20", 20)
		
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
		self.actuations += 1
		for roll in dice:
			self.die.add_roll(roll)
		self.chi_history.append(self.die.chi_squared())
		self.sf_vars["Actuations"].configure(text="{:d}".format(self.actuations))
		self.sf_vars["Dice Rolls"].configure(text="{:d}".format(self.die.rolls()))
		self.sf_vars["Average Roll"].configure(text="{:2.2f}".format(self.die.average()))
		self.sf_vars["Chi-Squared"].configure(text="{:2.2f}".format(self.chi_history[-1]))
		
		class FakeEvent:
			def __init__(self, width, height):
				self.width = width
				self.height = height
		self.canvas_chi.figure = graphs.chi_graph(self.chi_history)
		self.canvas_chi.resize(FakeEvent(self.graph_chi.winfo_width(), self.graph_chi.winfo_height()))
		self.canvas_bar.figure = graphs.count_graph(self.die)
		self.canvas_bar.resize(FakeEvent(self.graph_bar.winfo_width(), self.graph_bar.winfo_height()))
	
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

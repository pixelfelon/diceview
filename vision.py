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

import random
import threading
import cv2
from motion import Motion


class VisionThread(threading.Thread):
	def __init__(self, height=720, width=1280, camidx=0, group=None, target=None, name=None):
		super(VisionThread, self).__init__(group=group, target=target, name=name)
		
		self.camlock = threading.Condition()
		self.width, self.height = width, height
		self.camidx = camidx
		self._cap = None
		
		self.conlock = threading.Condition()
		self._apprun = True
		self._appstop = False
		self._sample = False
		
		self.reslock = threading.Condition()
		self.dice = []
		self.frame = None
		self.fresh = False
	
	def run(self):
		motion = Motion()
		_run = False
		_stop = False
		_sample = False
		
		with self.conlock:
			_run = self._apprun
			_stop = self._appstop
			_sample = self._sample
		
		while _run:
			self._cam_start()
			
			while True:
				with self.conlock:
					self.conlock.wait_for(lambda: (self._appstop or self._sample))
					_sample = self._sample
					_stop = self._appstop
				
				if _stop:
					break
				if not _sample:
					continue
				
				motion.roll()
				frame = self._get_frame()
				dice, frame = self._process_image(frame)
				
				with self.conlock:
					self._sample = False
				with self.reslock:
					self.dice = dice
					self.frame = frame
					self.fresh = True
					self.reslock.notify()
			
			self._cam_stop()
			with self.conlock:
				_run = self._apprun
	
	def stop(self):
		with self.conlock:
			self._apprun = False
			self._appstop = True
			self._sample = False
			self.conlock.notify()
	
	def restart(self):
		with self.conlock:
			self._apprun = True
			self._appstop = True
			self._sample = False
			self.conlock.notify()
	
	def sample(self):
		with self.conlock:
			self._apprun = True
			self._appstop = False
			self._sample = True
			self.conlock.notify()
	
	def wait_results(self):
		with self.reslock:
			if not self.fresh:
				self.reslock.wait_for(lambda: self.fresh)
			self.fresh = False
			dice = self.dice
			frame = self.frame
		return dice, frame
	
	def change_cam(self, camidx=0, width=1280, height=720):
		with self.camlock:
			self.camidx = camidx
			self.width = width
			self.height = height
		self.restart()
	
	def _cam_start(self):
		# Camera
		with self.camlock:
			width = self.width
			height = self.height
			camidx = self.camidx
		
		self._cap = cv2.VideoCapture(cv2.CAP_DSHOW + camidx)
		# time.sleep(1)
		self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
		self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
	
	def _cam_stop(self):
		self._cap.release()
		self._cap = None
	
	def _get_frame(self):
		_, frame = self._cap.read()
		return frame
	
	@staticmethod
	def _process_image(image):
		# Process an opencv image to find dice.
		# Will return two values:
		# - a list of 20-sided dice rolls.
		# - a version of the source image with additional cool markup.
		
		# Generate sample data.
		count = random.randrange(1, 4)
		out = []
		for i in range(count):
			roll = random.randrange(1, 21)
			out.append(roll)
		
		# Modify image.
		org = (int(image.shape[1] / 2), int(image.shape[0] / 2))
		cv2.putText(image, "Sample Text", org, cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 3, cv2.LINE_AA)
		
		return (out, image)

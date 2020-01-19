###############################################################################
# Project: Polyhedral Dice Statistical Analysis (Diceview)
# File   : cameras.py
#
# Multiple camera backends for different platforms.
#
# Copyright (c) 2020 Diceview Team
# Released under the MIT License.
#
#   Date      SCR  Comment                                        Eng
# -----------------------------------------------------------------------------
#   20200119       Created                                        jrowley
#
###############################################################################

import cv2
import platform


class BaseCam(object):
	def start(self):
		raise NotImplementedError()
	
	def stop(self):
		raise NotImplementedError()
	
	def get_frame(self):
		raise NotImplementedError()


class JetsonCam(BaseCam):
	def __init__(self):
		self._cap = None
	
	def start(self):
		self._cap = cv2.VideoCapture(self.gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
		if not self._cap.isOpened():
			print("Couldn't open camera!")
	
	def stop(self):
		self._cap.release()
		self._cap = None
	
	def ready(self):
		return self._cap is not None and self._cap.isOpened()
	
	def get_frame(self):
		_, frame = self._cap.read()
		c_size = 0.35
		w = int(frame.shape[1] * c_size)
		h = int(frame.shape[0] * c_size)
		x = int(frame.shape[1] * 0.5 - w * 0.5)
		y = int(frame.shape[0] * 0.5 - h * 0.5) + 50
		return frame[y:y + h, x:x + w]
	
	@staticmethod
	def gstreamer_pipeline(
			capture_width=3264,
			capture_height=2464,
			display_width=3264,
			display_height=2464,
			framerate=21,
			flip_method=0
	):
		return (
				"nvarguscamerasrc ! "
				"video/x-raw(memory:NVMM), "
				"width=(int)%d, height=(int)%d, "
				"wbmode=0, "
				"format=(string)NV12, framerate=(fraction)%d/1 ! "
				"nvvidconv flip-method=%d ! "
				"video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
				"videoconvert ! "
				"video/x-raw, format=(string)BGR ! appsink"
				% (
					capture_width,
					capture_height,
					framerate,
					flip_method,
					display_width,
					display_height
				)
		)


class USBCam(BaseCam):
	def __init__(self, camidx = 0):
		self._cap = None
		self._camidx = camidx
	
	def start(self):
		self._cap = cv2.VideoCapture(cv2.CAP_DSHOW + self._camidx)
		if not self._cap.isOpened():
			print("Couldn't open camera!")
		self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 100000)
		self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 100000)
	
	def stop(self):
		self._cap.release()
		self._cap = None
	
	def ready(self):
		return self._cap is not None and self._cap.isOpened()
	
	def get_frame(self):
		_, frame = self._cap.read()
		return frame


def get_best_cam():
	if platform.os.name == "nt":
		return USBCam
	else:
		return JetsonCam

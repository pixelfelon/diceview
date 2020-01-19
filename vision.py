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
import numpy as np
from collections import namedtuple

from motion import Motion
import cameras


# Params
DICE_SIZE = 250
CIRCLE_POS = (540, 460)
image_height, image_width = (862, 1142)
circle_mask = np.zeros((image_height, image_width), dtype=np.uint8)
circle_mask = cv2.circle(circle_mask, CIRCLE_POS, 470, 1, thickness=-1)


def subtract_and_mask(img, ref):
	img = cv2.absdiff(ref, img.copy())
	img = cv2.bitwise_and(img, img, mask=circle_mask)
	return img


class MatchWithSIFT(object):
	Referance_Points = namedtuple('Referance_Points', ['kp', 'des', 'img'])

	def __init__(self):
		self.sift = cv2.xfeatures2d.SIFT_create()
		self.bf = cv2.BFMatcher()
		self.ref_lib = dict()

	def add_ref(self, key, img):
		kp, des = self.sift.detectAndCompute(img, None)
		self.ref_lib[key] = self.Referance_Points(kp, des, img)

	def load_refs(self):
		for i in range(1, 20 + 1):
			self.add_ref(str(i), cv2.imread('{}-Grey.jpg'.format(i), 0))

	def knn_match(self, des1, des2):
		matches = self.bf.knnMatch(des1, des2, k=2)
		# Use the Lowe ratio test to filter matches
		return [m for (m, n) in matches if m.distance < 0.75 * n.distance]

	@staticmethod
	def find_homography(kp1, kp2, matches):
		src_points = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
		dst_points = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

		M, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC, 10.0)
		if mask is None:
			return [], [], 0

		match_mask = [[k, 0] for k in mask.ravel().tolist()]
		# Homography matrix, mask, inlier count
		return M, match_mask, np.count_nonzero(mask)

	def find_match(self, img):
		img_kp, img_des = self.sift.detectAndCompute(img, None)

		best_key = None
		best_score = None

		for key, value in self.ref_lib.items():
			matches = self.knn_match(value.des, img_des)

			if len(matches) < 2:
				# Very poor match
				continue

			M, matches_mask, inliers = self.find_homography(value.kp, img_kp, matches)

			if inliers < 10:
				# Poor match not enough matched points
				# continue
				pass

			try:
				test_out = cv2.drawMatches(img, img_kp, value.img, value.kp, matches, None)

				# cv2.imshow("Keypoint", test_out)
				# cv2.waitKey(0)
			except Exception as e:
				pass

			if inliers > best_score:
				best_score = inliers
				best_key = key

		return best_key


class VisionThread(threading.Thread):
	def __init__(self, group=None, target=None, name=None):
		super(VisionThread, self).__init__(group=group, target=target, name=name)
		
		self._cam = cameras.get_best_cam()()
		self._sift = None
		
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
		self._sift = MatchWithSIFT()
		self._sift.load_refs()
		
		_run = False
		_stop = False
		_sample = False
		
		with self.conlock:
			_run = self._apprun
			_stop = self._appstop
			_sample = self._sample
		
		while _run:
			self._cam.start()
			
			while self._cam.ready():
				with self.conlock:
					self.conlock.wait_for(lambda: (self._appstop or self._sample))
					_sample = self._sample
					_stop = self._appstop
				
				if _stop:
					break
				if not _sample:
					continue
				
				motion.roll()
				frame = self._cam.get_frame()
				dice, frame = self._process_image(frame)
				
				with self.conlock:
					self._sample = False
				with self.reslock:
					self.dice = dice
					self.frame = frame
					self.fresh = True
					self.reslock.notify()
			
			self._cam.stop()
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
	
	def change_cam(self):
		self.restart()
	
	def _process_image(self, image):
		# Process an opencv image to find dice.
		# Will return two values:
		# - a list of 20-sided dice rolls.
		# - a version of the source image with additional cool markup.
		img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		ref = cv2.imread('ref.jpg', 0)
	
		masked_img = subtract_and_mask(img, ref)
	
		# cv2.imshow('image', masked_img)
		# cv2.waitKey(0)
	
		ret, threshold_img = cv2.threshold(masked_img, 25, 255, cv2.THRESH_BINARY)
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
		threshold_img = cv2.morphologyEx(threshold_img, cv2.MORPH_OPEN, kernel)
	
		cv2.imshow('image', threshold_img)
		cv2.waitKey(0)
	
		# Setup SimpleBlobDetector parameters.
		params = cv2.SimpleBlobDetector_Params()
	
		params.blobColor = 255
		params.filterByColor = True
		params.filterByArea = True
		params.minDistBetweenBlobs = 2
		params.minArea = 2000
		# Blobs larger than 50 pixels are noise
		params.maxArea = 50000
		# enabling these can cause us to miss points
		params.filterByCircularity = False
		params.filterByConvexity = False
		params.filterByInertia = False
	
		# Create a detector with the parameters
		detector = cv2.SimpleBlobDetector_create(params)
	
		# Detect blobs.
		keypoints = detector.detect(threshold_img)
	
		out_arr = list()
	
		for i, point in enumerate(keypoints):
			y, x = point.pt
			found_dice = image[int(x - DICE_SIZE * 0.5):int(x - DICE_SIZE * 0.5 + DICE_SIZE), int(y - DICE_SIZE * 0.5):int(y - DICE_SIZE * 0.5 + DICE_SIZE)]
			found_hsv = cv2.cvtColor(found_dice, cv2.COLOR_BGR2HSV)
			dice_grey = cv2.cvtColor(found_dice, cv2.COLOR_BGR2GRAY)
			die_num = self._sift.find_match(dice_grey)
			if die_num is not None:
				out_arr.append(int(die_num))
			# img_col = cv2.putText(img_col, str(die_num), (int(y) - 10, int(x) + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
			# cv2.imshow("Keypoint", found_dice)
			# cv2.waitKey(0)
	
		# Draw detected blobs as red circles.
		# cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
		image = cv2.drawKeypoints(threshold_img, keypoints, np.array([]), (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
	
		cv2.imshow('image', image)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		return out_arr, image

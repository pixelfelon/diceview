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

import tkinter
import cv2
from PIL import Image, ImageTk


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
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("diceview")
        self.root.state("zoomed")
        self.root.focus_set()

        self.root.configure(bg="#555")
        self.cframe = tkinter.Frame(self.root, bg="#555", width=200)
        self.cframe.pack(fill=tkinter.Y, padx=10, side=tkinter.LEFT)
        self.cframe.pack_propagate(0)

        self.vframe = tkinter.Label(self.root, bd=0, bg='#222')
        self.vframe.pack(fill="both", expand=True)

        # Camera
        self.width, self.height = 1280, 720
        self.cap = cv2.VideoCapture(0)
        time.sleep(3)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.get_frame()

    def get_frame(self):
        _, frame = self.cap.read()
        frame = cv2.flip(frame, 1)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        size = clamp_aspect(16.0 / 9.0, self.vframe.winfo_width(), self.vframe.winfo_height())
        frame = cv2.resize(frame, size)
        frame = Image.fromarray(frame)
        frame = ImageTk.PhotoImage(frame)
        self.vframe.configure(image=frame)
        self.vframe.image = frame

        self.root.after(10, self.get_frame)

    def shutdown(self):
        self.cap.release()
        self.root.destroy()
        os._exit(0)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.root.mainloop()


if __name__ == "__main__":
    app = DiceviewApp()
    app.run()

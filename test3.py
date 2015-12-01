# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 15:08:12 2015

@author: uluyac
"""

import cv2
from Tkinter import Tk
from tkFileDialog import askopenfilename
import numpy as np
from mpegCodec.utils import frame_utils as futils

root = Tk()
root.withdraw()

sequence = []

vdName = askopenfilename(parent=root, title="Enter with a video file.").__str__()
print("\nFile: " + vdName)

video = cv2.VideoCapture(vdName)

ret, fr = video.read()
sequence.append(fr)

while ret:
    ret, fr = video.read()
    if ret != False:
        sequence.append(fr)
video.release()
    
futils.write_sequence_frames(sequence)
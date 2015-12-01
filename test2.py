# -*- coding: utf-8 -*-
"""
Created on Mon May 25 16:04:07 2015

@author: luan
"""

from mpegCodec import codec
from mpegCodec.utils import frame_utils as futils

from Tkinter import Tk
from tkFileDialog import askopenfilename

root = Tk()
root.withdraw()
#Tk().withdraw()

### ENCODER ###
#vdName = askopenfilename(parent=root, title="Enter with a video file.").__str__()
#print("\nFile: " + vdName)
#mpeg = codec.Encoder(vdName, quality = 75, sspace = 16, mode = '444', search = 1, hvsqm = 1, flat = 10.0, p = 2.0)
#mpeg.run()

### DECODER ###
fileName = askopenfilename(parent=root, title="Enter with a video file.").__str__()
print("\nFile: " + fileName)
mpeg = codec.Decoder(fileName)
seq = mpeg.run()
futils.write_sequence_frames(seq, fileName)
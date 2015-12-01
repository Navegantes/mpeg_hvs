# -*- coding: utf-8 -*-
"""
Created on Mon May 25 16:04:07 2015

@author: luan
"""

from mpegCodec import codec
from mpegCodec.utils import frame_utils as futils

from Tkinter import Tk
from tkFileDialog import askopenfilename
import sys

root = Tk()
root.withdraw()
#Tk().withdraw()

fileName = askopenfilename(parent=root, title="Enter with a video file.").__str__()
if fileName == '': 
    sys.exit('Filename empty!')
print("\nFile: " + fileName)
name = fileName.split('/')
print name
name = name[-1]
print name
name = name.split('.')[-1]
print name
if name == 'mp4' or name == 'MP4' or name == 'avi' or name == 'AVI':
    mpeg = codec.Encoder(fileName, quality = 50, sspace = 16, mode = '420', search = 1, hvsqm = 0, flat = 10.0, p = 2.0)
    mpeg.run()
elif name == 'txt' or name == 'TXT':
    mpeg = codec.Decoder(fileName)
    seq = mpeg.run()
    futils.write_sequence_frames(seq, fileName)
else:
    print('Invalid filename!!!!')
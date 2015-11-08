# -*- coding: utf-8 -*-
"""
Created on Mon May 25 16:04:07 2015

@author: luan
"""

# Teste commit

from mpegCodec import codec

from Tkinter import Tk
from tkFileDialog import askopenfilename

root = Tk()
root.withdraw()
#Tk().withdraw()

### ENCODER ###
#vdName = askopenfilename(parent=root, title="Enter with a video file.").__str__()
#mpeg = codec.Encoder(vdName, quality = 75, sspace = 16, mode = '420', search = 1, hvsqm = 1, flat = 10.0, p = 2.0)
#mpeg.run()

### DECODER ###
vdName = askopenfilename().__str__()
mpeg = codec.Decoder(vdName)
mpeg.run()
# -*- coding: utf-8 -*-
"""
Created on Mon May 25 16:04:07 2015

@author: luan
"""

from mpegCodec import codec
from mpegCodec.utils import frame_utils as futils
from image_quality_assessment import metrics

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
name = name[-1]
name = name.split('.')[-1]

quality = 50	# Compression quality.
sspace = 32	# Search space.
search = 1		# 0 - Full search; 1 - Parallel hierarchical.
flat = 10.0	# Qflat value.
p = 2.0		# Parameter p.
files = 1	

if name == 'mp4' or name == 'MP4' or name == 'mpg'or name == 'avi' or name == 'AVI':
	if files == 0:
		for hvsqm in range(2):
			for mode in ['444','420']:
				print 'HVS = %d mode = %s' %(hvsqm, mode)
				mpeg = codec.Encoder(fileName, quality, sspace, mode, search, hvsqm, flat, p)
				mpeg.run()
				if hvsqm == 0:
					filetxt = './outputs/normal/' + mode + '/' + fileName.split('/')[-1].split('.')[0] + '.txt'
				else:
					filetxt = './outputs/hvs/' + mode + '/' + fileName.split('/')[-1].split('.')[0] + '_hvs' + '.txt'
				mpeg = codec.Decoder(filetxt)
				seq = mpeg.run()
				futils.write_sequence_frames(seq, mpeg.mode, mpeg.hvsqm, filetxt)
	else:
		mpeg = codec.Encoder(fileName, quality = 50, sspace = 16, mode = '444', search = 1, hvsqm = 0, flat = 10.0, p = 2.0)
		mpeg.run()
				
elif name == 'txt' or name == 'TXT':
	mpeg = codec.Decoder(fileName)
	seq = mpeg.run()
	futils.write_sequence_frames(seq, mpeg.mode, mpeg.hvsqm, fileName)
else:
	print('Invalid filename!!!!')
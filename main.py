# -*- coding: utf-8 -*-
"""
Created on Mon May 25 16:04:07 2015

@author: luan
"""

from mpegCodec import codec
from mpegCodec.utils import frame_utils as futils
import matplotlib.pylab as plt
from Tkinter import Tk
from tkFileDialog import askopenfilename
import sys
import numpy as np

root = Tk()
root.withdraw()

fileName = askopenfilename(parent=root, title="Enter with a file name.").__str__()
if fileName == '': 
    sys.exit('Filename empty!')
print("\nFile: " + fileName)
name = fileName.split('/')
print name
name = name[-1]
print name
name = name.split('.')[-1]
print name

# In order to run the encoder just enter with a video file.
# In order to run the decoder just enter with a output file (in the output directory).

files = 0       # 0 - Runs all encoder modes for a given video (normal - 444 and 420, hvs - 444 and 420)
                # 1 - Runs encoder for a given video with the following setup.

quality = 50    # Compression quality.
sspace = 32    # Search space.
search = 1        # 0 - Full search; 1 - Parallel hierarchical.
flat = 10.0    # Qflat value.
p = 2.0        # Parameter p.

if name == 'mp4' or name == 'MP4' or name == 'mpg'or name == 'avi' or name == 'AVI':
    if files == 1:
        for hvsqm in range(2):
            for mode in ['444','420']:
                print 'HVS = %d mode = %s' %(hvsqm, mode)
                mpeg = codec.Encoder(fileName, quality, sspace, mode, search, hvsqm, flat, p)
                mpeg.run()
                if hvsqm == 0:
                    filetxt = './outputs/normal/' + mode + '/' + fileName.split('/')[-1].split('.')[0] + '.txt'
                else:
                    filetxt = './outputs/hvs/' + mode + '/' + fileName.split('/')[-1].split('.')[0] + '.txt'
                mpeg = codec.Decoder(filetxt)
                seq = mpeg.run()
                futils.write_sequence_frames(seq, mpeg.mode, mpeg.hvsqm, filetxt)
    else:
        mpeg = codec.Encoder(fileName, quality = 50, sspace = 16, mode = '420', search = 1, hvsqm = 1, flat = 10.0, p = 2.0)
        mpeg.run()
                
elif name == 'txt' or name == 'TXT':
    videoName = askopenfilename(parent=root, title="Enter with the original video file.").__str__()
    mpeg = codec.Decoder(fileName, videoName)
    seq, psnrValues, msimValues = mpeg.run()
    futils.write_sequence_frames(seq, mpeg.mode, mpeg.hvsqm, fileName)
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    psnrMean = np.mean(np.array(psnrValues)[:,0])
    ax1.plot(range(len(psnrValues)), np.array(psnrValues)[:,0], '-*',label="Values",)
    ax1.plot(range(len(psnrValues)), np.ones(len(psnrValues))*psnrMean, '-p',label="Mean")
    legend1 = ax1.legend(loc='upper right', shadow=True)
    ax1.set_xlabel("Frames")
    ax1.set_ylabel("psnr")
    ax1.set_title("PSNR")
    ax1.grid()

    ax2 = fig.add_subplot(212)
    msimMean = np.mean(np.array(msimValues)[:,0])
    ax2.plot(range(len(msimValues)),np.array(msimValues)[:,0], '-*', label="Values")
    ax2.plot(range(len(msimValues)), np.ones(len(msimValues))*msimMean, '-p', label="Mean")
    legend2 = ax2.legend(loc='upper right', shadow=True)
    ax2.set_xlabel("Frames")
    ax2.set_ylabel("msim")
    ax2.set_title("MSIM")
    ax2.grid()
    plt.subplots_adjust(hspace=0.3)
else:
    print('Invalid filename!!!!')
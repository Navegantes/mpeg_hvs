# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 14:41:38 2015

@author: uluyac
"""

import cv2
import os

from Tkinter import Tk
from tkSimpleDialog import askstring

def sequence_iterator(sequence):
    
    nFrames = len(sequence)
    wName = 'Video'
    cv2.namedWindow(wName)
    
    print '\n### Sequence Iterator ###'
    print 'Number of frames: ' + str(nFrames)
    for i in range(nFrames):
        cv2.imshow('Video', sequence[i])
        cv2.waitKey(0)
        
    cv2.destroyAllWindows()
    
    
def write_sequence_frames(sequence, video_name = ''):
    
    root = Tk()
    root.withdraw()
    
    nFrames = len(sequence)
    wName = 'Video'
    cv2.namedWindow(wName)
    
    dirName = ''
    if video_name == '':
        dirName = askstring("Directory Name", "Enter with the directory output name").__str__()
    else:
        dirName = video_name.split('/')
        str_len = len(dirName)
        dirName = dirName[str_len-1]
        dirName = dirName.split('.')[0]
        
    dirName = ''.join(e for e in dirName if e.isalnum())
    directory = './frames_output/' + dirName + '/'
    extension = '.png'
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    print '\n### Writing frames ###'
    print 'Number of frames: ' + str(nFrames)
    for i in range(nFrames):
        imName = directory + str(i) + extension
        print('Saving ' + imName)
        cv2.imwrite(imName, sequence[i])
    
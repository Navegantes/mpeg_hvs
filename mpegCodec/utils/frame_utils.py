# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 14:41:38 2015

@author: uluyac
"""

import cv2
import os

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
    
    
def write_sequence_frames(sequence, video_name):
    
    nFrames = len(sequence)
    wName = 'Video'
    cv2.namedWindow(wName)
    
    splited = video_name.split('/')
    str_len = len(splited)
    splited = splited[str_len-1]
    splited = splited.split('.')[0]
    directory = './frames_output/' + splited + '/'
    extension = '.png'
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    print '\n### Writing frames ###'
    print 'Number of frames: ' + str(nFrames)
    for i in range(nFrames):
        imName = directory + str(i) + extension
        print('Saving ' + imName)
        cv2.imwrite(imName, sequence[i])
    
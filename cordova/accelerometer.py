import time
import logging
import random
import os
import sys


class Accelerometer(object):
    def getCurrentAcceleration(self,args):
        timestamp = time.time()
        accelerometer_obj = {'x':random.uniform(1, 10),'y':random.uniform(1, 10),'z':random.uniform(1, 10),'timestamp':timestamp,'keepCallback':True}
        return accelerometer_obj


def accelerometer_obj():
    
    timestamp = time.time()
    accelerometer_obj = {'x':random.uniform(1, 10),'y':random.uniform(1, 10),'z':random.uniform(1, 10),'timestamp':timestamp,'keepCallback':True}
    return accelerometer_obj
    """

    
    timestamp = time.time()

    # accelerometer code from : https://git.sugarlabs.org/maze/mainline/blobs/master/sensors.py

    ACCELEROMETER_DEVICE = '/sys/devices/platform/lis3lv02d/position'
    
    
    # return x, y, z values or None if no accelerometer is available
    
    try:
        fh = open(self.ACCELEROMETER_DEVICE)
        string = fh.read()
        xyz = string[1:-2].split(',')
        fh.close()
        #return int(xyz[0]), int(xyz[1]), int(xyz[2])
        accelerometer_obj = {'x':int(xyz[0]),'y':int(xyz[1]),'z':int(xyz[2]),'timestamp':timestamp,'keepCallback':True}
        return accelerometer_obj
    except:
        #return 0, 0, 0
        accelerometer_obj = {'x':0,'y':0,'z':0,'timestamp':timestamp,'keepCallback':True}
        return accelerometer_obj
    """

import sys

if sys.version_info  < ( 2, 7):

    import unittest2 as unittest
else:

    import unittest


if sys.version_info  < ( 3,0):

    import urlparse
##    import ConfigParser

    import xml.etree.ElementTree as ET
else:

    import urllib.parse as urlparse
##    import configparse
    import lxml.etree as ET





import os

import posixpath



import time



import random

import numpy as np

from skimage import measure

from bqapi import *

from bqapi.util import save_blob
from bqapi.util import fetch_blob



from skimage.io import imread

from skimage import measure

from matplotlib import pyplot as plt

import pdb

import nibabel as nib
import skimage.io as io
import numpy as np



def find_contour(seg_name):
        
    img=nib.load(seg_name)
    img_arr=img.get_fdata()

    z=img_arr.shape[2]
    for i in range(z):
        cur_layer=img_arr[:,:,i]
        contours=list(measure.find_contours(cur_layer, 0.5))
        
    return contours


def gobject_core(seg_name, meta):

    root=meta
    img=nib.load(seg_name)
    img_arr=img.get_fdata()

    z=img_arr.shape[2]

    for j in range(z):

        cur_layer=img_arr[:,:,j]
        contours=list(measure.find_contours(cur_layer, 0.5))
        
        if contours:
            for k in range(len(contours)):
                polygon = ET.SubElement(root, 'polygon')
                for i in range(len(contours[k])):

                    vertex = ET.SubElement(polygon, 'vertex')

                    vertex.set('index', str(i))

                    vertex.set('t', str(0.0))

                    vertex.set('x', str(contours[k][i][0]))

                    vertex.set('y', str(contours[k][i][1]))

                    vertex.set('z', str(float(j)))

    return root

def main():
    
    root='https://bisque.ece.ucsb.edu'

    user =''

    pswd =''


    bq = BQSession().init_local(user, pswd,  bisque_root=root, create_mex=False)


    imageURL='https://bisque.ece.ucsb.edu/data_service/00-LP8E4k4srt9BwkeVdENjRb'
    annotationURL='https://bisque.ece.ucsb.edu/data_service/00-LAmrRHbMXKGwsQ4eYYQRcj'

    seg = bq.load(annotationURL)
    seg_name=seg.__dict__['name']
        
    cwd= os.getcwd()

    result = fetch_blob(bq, annotationURL, dest=os.path.join(cwd,seg_name))
        
    if '.gz' in seg_name:
        os.rename(seg_name,seg_name.replace('.gz',''))
        seg_name=seg_name.replace('.gz','')
        
    meta = bq.fetchxml('%s?meta'%imageURL)
    xml_new=gobject_core(seg_name, meta)

    bq.postxml(imageURL, xml_new, method='POST')

    print('result uploaded')

        

if __name__=='__main__':


    main()

##MetaData
    

    






    

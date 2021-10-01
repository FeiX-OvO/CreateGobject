import sys

if sys.version_info  < ( 2, 7 ):

    import unittest2 as unittest

else:

    import unittest

import os

import posixpath

import urlparse

import time

import ConfigParser

import random

import numpy as np

from skimage import measure

from bqapi import *

from bqapi.util import save_blob

import xml.etree.ElementTree as ET

from skimage.io import imread

from skimage import measure

from matplotlib import pyplot as plt

import pdb

import nibabel as nib
import skimage.io as io
import numpy as np


class AddAnnotations():
    def find_contour(seg_name):
            
        img=nib.load(seg_name)
        img_arr=img.get_fdata()

        z=img_arr.shape[2]
        for i in range(z):
            cur_layer=img_arr[:,:,i]
            contours=list(measure.find_contours(cur_layer, 0.5))
            
        return contours


    def gobject_core(seg_name, meta):

    ##    img=nib.load(seg_name)
    ##    img_arr=img.get_fdata()
    ##    cur_layer=img_arr[:,:,14]
    ##    contours=measure.find_contours(cur_layer, 0.5)
    ##    print(contours)
        

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

    user ='fei_xu'

    pswd ='ZeroMiao1010'


    folder='/Users/zero/Downloads/COVID-19-20_v2/Train/Annotation/'
    
    dataset_uri = 'https://bisque.ece.ucsb.edu/data_service/00-RpV7oiCiFx2VdqP4TUcam8'


    session = BQSession().init_local(user, pswd,  bisque_root=root, create_mex=False)

    dataset_meta = session.fetchxml('%s?view=deep'%dataset_uri)
##    image_uri='https://bisque.ece.ucsb.edu/data_service/00-ggF2CkEzDi8UKVP5DNhjeE'
##    image = session.load(image_uri)
    index=0
    for item in dataset_meta.__dict__['_children']:

        print('reading'+str(index))
        
        image_uri=item.__dict__['text']

        print(image_uri)
        image = session.load(image_uri) 
        image_name=image.name
        seg_name='_seg'.join(image_name.split('_ct'))

        seg_name=folder+seg_name
        print(seg_name)
        
        meta = session.fetchxml('%s?meta'%image_uri)
        

        xml_new=gobject_core(seg_name, meta)
        print(xml_new)

        session.postxml(image_uri, xml_new, method='POST')
        print('uploaded', seg_name)

        print(session.fetchblob(image_uri))
        
        

if __name__=='__main__':


    main()

##MetaData
    

    






    

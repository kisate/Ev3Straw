import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')

import cv2
import numpy as npy

img_arr = []

for i in range(8):
    dest = 'images/{}.png'.format(i + 1)
    print(dest)
    img = cv2.imread(dest,0)
    r = 500.0 / img.shape[1]
    dim = (500, int(img.shape[0] * r))
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    print ("add new img")
    img_arr.append(img)
numpy_vertical1 = npy.hstack(img_arr[:4])
numpy_vertical2 = npy.hstack(img_arr[4:])
numpy_hor= npy.vstack((numpy_vertical1, numpy_vertical2))
#cv2.imshow('Numpy Vertical', numpy_vertical1)
#cv2.imshow('Numpy Horisontal', numpy_vertical2)
cv2.imshow('Hot', numpy_hor)
cv2.waitKey(0)

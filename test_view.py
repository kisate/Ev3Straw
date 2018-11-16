import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')

import cv2
import numpy as npy

img_arr = []
l = 14


for i in range(l):
    dest = 'images/image{}.png'.format(i)
    print(dest)
    img = cv2.imread(dest,1)
    r = 500.0 / img.shape[1]
    dim = (500, int(img.shape[0] * r))
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    print ("add new img")
    img_arr.append(npy.array(img))


numpy_vertical1 = npy.column_stack(img_arr[:l//2])
cv2.imshow('Numpy Vertical', numpy_vertical1)
# numpy_vertical2 = npy.hstack(img_arr[l//2:])
# cv2.imshow('Numpy Horisontal', numpy_vertical2)
# numpy_hor= npy.column_stack((img_arr[:l//2], img_arr[l//2:]))
# cv2.imshow('Hot', numpy_hor)
cv2.waitKey(0)

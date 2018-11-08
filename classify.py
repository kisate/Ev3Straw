
import sys

sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')

import tensorflow as tf
import numpy  as np
import glob, os
import time
import cv2
import pickle
from PIL import Image

class Classifier(object):
    def __init__(self):
        PATH_TO_MODEL = r'/home/forester/Documents/klubnikor/export7/frozen_inference_graph.pb'
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_MODEL, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
            self.d_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
            self.d_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            self.d_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_d = self.detection_graph.get_tensor_by_name('num_detections:0')
        self.sess = tf.Session(graph=self.detection_graph)


    def get_classification(self, img):
        with self.detection_graph.as_default():
            img_expanded = np.expand_dims(img, axis=0)  
            (boxes, scores, classes, num) = self.sess.run(
                [self.d_boxes, self.d_scores, self.d_classes, self.num_d],
                feed_dict={self.image_tensor: img_expanded})
        return boxes, scores, classes, num

def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

classifier = Classifier()

while(True):
    res = glob.glob("../photos/img.png")

    print(res)

    while (len(res) == 0) :
        res = glob.glob("../photos/img.png")
        time.sleep(0.003)

    print(res[0])

    img = cv2.imread(res[0])

    print(img)

    cv2.imshow("neuro", img)

    image = Image.open(res[0])
  # the array based representation of the image will be used later in order to prepare the
  # result image with boxes and labels on it.
    image_np = load_image_into_numpy_array(image)

    data = classifier.get_classification(image_np)
    print(data)

    #data = [[1, 2, 3], [4, 5, 6]]

    f = open("../photos/classes.out", 'wb')

    pickle.dump(data, f, protocol=2)

    f.close()

    os.remove(res[0])
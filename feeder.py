import sys

sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')


import cv2
import glob, os
import time
import pickle

colormap = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]


for path in glob.glob("../../dataset6/*.png"):
    print(path)
    img = cv2.imread(path)
    cv2.imshow("image", img)   

    k = cv2.waitKey(0)
    if k == ord('a'):
        cv2.imwrite("../photos/imgt.png", img)
        os.rename("../photos/imgt.png", "../photos/img.png")
        frame = cv2.imread("../photos/img.png")
        cv2.imshow("frame", frame)
        response = glob.glob('../photos/classes.out')
        while (len(response) == 0):
            response = glob.glob('../photos/classes.out')
            time.sleep(0.01)

        f = open("../photos/classes.out", "rb")
        
        data = pickle.load(f)

        f.close()

        boxes, scores, classes, num_classes = data

        height, width, _ = frame.shape
        
        print(boxes)

        for index in range(int(num_classes[0])):
            if (scores[0][index] > 0.2):
                box = boxes[0][index]
                classID = int(classes[0][index])
                pointA, pointB = (int(box[1]*width), int(box[0]*height)), (int(box[3]*width), int(box[2]*height))
                cv2.rectangle(frame, pointA, pointB, colormap[classID-1], 4)

        cv2.imshow("frame", frame)

        os.remove("../photos/classes.out")
        print(response)

    if k == ord('q'):
        cv2.destroyAllWindows()
        break
        
    
    # uploaded_image = im.upload_image("../photos/img{}.png".format(i), title="Strawberry {}".format(i))
   

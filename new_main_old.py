import cv2 
import numpy as npy
import socket 
import time
import threading
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pyimgur
import struct
import os, glob, pickle
import logging 
<<<<<<< HEAD:new_main.py
=======
import traceback
>>>>>>> e1b8e6c46df699a238b1a95f3208465efbf19638:new_main_old.py
from getkey import getkey, keys
from time import sleep
import tellopy
from wireless import Wireless

imHeight = 480
height = 20.5

host = '192.168.1.3'
port = 51100 # random number
a = True

q = []

changed_id = []
changed_stats = []
CLIENT_ID = "733b83d64f87370"

state = 0

#endPos = -10000
endPos = -10000

first = -1
notBerryCount = 0

collected = 0 
delivering = False
switched = False
readyToDeliver = False
readyToFly = False
cameraId = 1

pos = 0
<<<<<<< HEAD:new_main.py
cap = cv2.VideoCapture(6)
=======
>>>>>>> e1b8e6c46df699a238b1a95f3208465efbf19638:new_main_old.py

cv2.namedWindow('image')

low1 = npy.array([0, 130, 90])
high1 = npy.array([15, 255, 255])
low2 = npy.array([165, 130, 90])
high2 = npy.array([180, 255, 255])

low3 = npy.array([69, 100, 120])
high3 = npy.array([75, 200, 220])

colormap = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

berries = [[],[]]
allberries = []

switch = 0
lastid = -1

wireless = Wireless()

def tello_handler(event, sender, data, **args):
    drone = sender
    
    if event is drone.EVENT_FLIGHT_DATA:
        print(data)
        drone.down(0)
        alt = int(str(data).split("=")[1].split(",")[0])
        #print(alt)

########################################################33
#check socket connetion
# drone = tellopy.Tello()
# drone.subscribe(drone.EVENT_FLIGHT_DATA, tello_handler)
# drone.connect()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try : 
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
except Exception:
    pass

s.bind(('', port))
s.listen(5)

########################################################

def close():
    exit()

#init database 

def initialize():
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://strawberryfinder.firebaseio.com/',
        'databaseAuthVariableOverride': {
            'uid': 'firebase-adminsdk-z6zvt@strawberryfinder.iam.gserviceaccount.com'
        }
    })
    return db.reference('/berrys')

#create new element in database

def create_new(ref, enc, n, price, status, url,  x, y, classID, half):
    ref.child(str(n)).set({
        'encoder' : enc,
        'id' : n,
        'price' : price,
        'status' : str(status),
        'url' : url,
        'x' : x,
        'y' : y,
        'classID' : classID,
        'half' : half
    })    

#update status of strawberry

def update_status(ref, n, status):
    ref.child(str(n)).update({
        'status': str(status),
    })

#change state of machine

def handleMessage(message):
    global pos, delivering, switched, readyToDeliver, readyToFly
    if message[0] == 1:
        pos = message[1]
    if message[0] == 2:
        delivering = False
    if message[0] == 3:
        switched = True
    if message[0] == 4:
        readyToDeliver = True
    if message[0] == 5:
        readyToFly = True
    

def reader():
    global conn
    
    while a:
        message = []

        part = conn.recv(1)
        
        if (len(part) == 0):
            conn.close()
            break

        message_size = struct.unpack('>b', part)[0]

        #print "{} {}".format(part, struct.unpack('>b', part))

        for i in range(message_size):
            part = conn.recv(8)
            
            #print "{} {}".format(part, struct.unpack('>q', part))
            message.append(struct.unpack('>q', part)[0])
            #message.append(int.from_bytes(part, byteorder='big', signed=True))

        handleMessage(message)
        if len(part) == 0 : break

#send to ev3

def send(*args):
        
    #msg = len(args).to_bytes(1, byteorder='big')
    msg = struct.pack('>b', len(args))

    for a in args:
        #msg += (int(a)).to_bytes(8, byteorder='big', signed=True)
        msg += struct.pack('>q', a)

    conn.send(msg)

threading.Thread(target=reader, args=()).start()

<<<<<<< HEAD:new_main.py
=======
while state != 6:
    try : 
        if state == 1:
            cap = cv2.VideoCapture(cameraId)
            send(3, endPos)

            while(pos > endPos):
                # Capture frame-by-frame    
                ret, frame = cap.read()
                
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                
                mask = cv2.inRange(hsv, low1, high1)
                mask += cv2.inRange(hsv, low2, high2)    
                #mask += cv2.inRange(hsv, low3, high3)
>>>>>>> e1b8e6c46df699a238b1a95f3208465efbf19638:new_main_old.py

while state != 6:
    ret, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if state == 1:
        while(pos > endPos):
            # Capture frame-by-frame    
            
            mask = cv2.inRange(hsv, low1, high1)
            mask += cv2.inRange(hsv, low2, high2)    
            #mask += cv2.inRange(hsv, low3, high3)

            cv2.bitwise_and(hsv, hsv, mask = mask)
            connectivity = 7
            output = cv2.connectedComponentsWithStats(mask, connectivity, cv2.CV_32S)
            
            num_labels = output[0]
            labels = output[1]
            stats = output[2]
            centroids = output[3]
                        
            del berries[(switch + 1)%2][:]
            for i in range(num_labels):
                x, y, w, h, s = stats[i]
                if s > 2500 and s < 50000 and y > 50 and y < 100:            
                    sx = hex(x)[2:].zfill(4) 
                    sy = hex(y)[2:].zfill(4) 

                    croped = frame[max(int(centroids[i][1] - 200), 0):int(centroids[i][1])+200, max(int(centroids[i][0]) - 200, 0):int(centroids[i][0])+200]   
                    #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),3)    
                    cv2.circle(frame,(int(centroids[i][0]), int(centroids[i][1])), 10, (0,255,0), -1)

                    a = 2500
                    b = -1

                    for berry in berries[(switch)%2]:    
                        r = (berry['x'] - centroids[i][0])**2 + (berry['y'] - centroids[i][1]) 
                        if r < a:
                            a = r
                            b = berry['id']        
                    if b == -1:
                        lastid+=1
                        berries[(switch + 1)%2].append({'x' : centroids[i][0], 'y' : centroids[i][1], 'id' : lastid})

                        allberries.append({'x' : centroids[i][1], 'y' : centroids[i][0], 'id' : lastid, 'enc' : pos, 'frame' : frame, 'half' : 1})

                        #allberries.append({'x' : centroids[i][1], 'y' : centroids[i][0], 'id' : lastid, 'enc' : pos, 'frame' : frame[max(int(centroids[i][1] - 200), 0):int(centroids[i][1])+200, max(int(centroids[i][0]) - 200, 0):int(centroids[i][0])+200]})
                        #allberries.append({'x' : centroids[i][0], 'y' : centroids[i][1], 'id' : lastid, 'enc' : 311})
                    else :
                        berries[(switch + 1)%2].append({'x' : centroids[i][0], 'y' : centroids[i][1], 'id' : b})
            switch=(switch + 1)%2
            cv2.imshow('image', frame)
        state = 2
    if state == 2:
        ref = initialize()
        im = pyimgur.Imgur(CLIENT_ID)

        db.reference('/berrys').delete()
        for i, berry in enumerate(allberries):
            
            frame = berry['frame']

            #cv2.imshow("image{}".format(i), frame)   
            
            cv2.imwrite("../photos/imgt.png", frame)
            os.rename("../photos/imgt.png", "../photos/img.png")
            
            print i

            response = glob.glob('../photos/classes.out')
            while (len(response) == 0):
                response = glob.glob('../photos/classes.out')
                time.sleep(0.03)

            f = open("../photos/classes.out", "rb")
            
            data = pickle.load(f)

<<<<<<< HEAD:new_main.py
            f.close()

            boxes, scores, classes, num_classes = data

            height, width, _ = frame.shape
            
            res = None

            for index in range(int(num_classes[0])):
                if (scores[0][index] > 0.2):
                    box = boxes[0][index]
                    classID = int(classes[0][index])
                    pointA, pointB = (min(int(box[1]*width), int(box[3]*width)), min(int(box[0]*width), int(box[2]*width))), (max(int(box[1]*width), int(box[3]*width)), max(int(box[0]*width), int(box[2]*width)))
                    cv2.rectangle(frame, pointA, pointB, colormap[classID-1], 4)
                    
                    print (str(pointA))
=======
            cap.release()
            print "done"

            state = 2
        if state == 2:
            cv2.namedWindow("output")
            ref = initialize()
            im = pyimgur.Imgur(CLIENT_ID)
>>>>>>> e1b8e6c46df699a238b1a95f3208465efbf19638:new_main_old.py

                    print (str(pointB))

<<<<<<< HEAD:new_main.py
                    print ("{} {}".format(berry['x'], berry['y']))

                    #print "Berry {} minx: {} maxx: {} x : {} \nminy: {} maxy: {} y : {} \n".format(min(pointA[0], pointB[0]), max(pointA[0], pointB[0]), berry['x'], min(pointA[1], pointB[1]),  max(pointA[1], pointB[1]), berry['y'] )
                    
                    if (pointA[0] < berry['y'] < pointB[0] and pointA[1] < berry['x'] < pointB[1]):
                        #res = {'classID' : classID, 'x' : int((pointA[1] + pointB[1]) / 2), 'y' : int((pointA[0] + pointB[0]) / 2)}
                        res = {'classID' : classID, 'x' : berry['x'], 'y' : berry['y']}
                        print "yep{}".format(index)
=======
                #cv2.imshow("image{}".format(i), frame)   
                

                cv2.imwrite("../photos/imgt.png", frame)
                os.rename("../photos/imgt.png", "../photos/img.png")
                print i
                  
                response = glob.glob('../photos/classes.out')
                while (len(response) == 0):
                    response = glob.glob('../photos/classes.out')
                    time.sleep(0.03)
>>>>>>> e1b8e6c46df699a238b1a95f3208465efbf19638:new_main_old.py

            #cv2.imshow("image{}".format(i), frame)

            cv2.imwrite("../neurooutput/image{}.png".format(i), frame)

            os.remove("../photos/classes.out")
            
            if res is not None:

                # uploaded_image = im.upload_image("../photos/img{}.png".format(i), title="Strawberry {}".format(i))
                
<<<<<<< HEAD:new_main.py
                link = 'https://i.imgur.com/CQdaHBw.png'
=======
                res = None

                for index in range(int(num_classes[0])):
                    if (scores[0][index] > 0.2):
                        box = boxes[0][index]
                        classID = int(classes[0][index])

                        coef1 = 0.75
                        coef2 = 0.75

                        pointA, pointB = (min(int(box[1]*width), int(box[3]*width)), min(int(box[0]*width*coef1), int(box[2]*width*coef1))), (max(int(box[1]*width), int(box[3]*width)), max(int(box[0]*width*coef2), int(box[2]*width*coef2)))
                        cv2.rectangle(frame, pointA, pointB, colormap[classID-1], 4)
                        
                        print (str(pointA))
>>>>>>> e1b8e6c46df699a238b1a95f3208465efbf19638:new_main_old.py

                # print(uploaded_image.link)
                create_new(ref, -berry['enc'], i+1, 100, 0, str(link), res['x'], res['y']/imHeight*height, res['classID'], berry['half'])

                print "created"
                # create_new(ref, -berry['enc'], i+1, 100, 0, str(uploaded_image.link), int(berry['x']), berry['y']/imHeight*height)
            else :
                link = 'https://i.imgur.com/CQdaHBw.png'

<<<<<<< HEAD:new_main.py
                # print(uploaded_image.link)
                create_new(ref, -berry['enc'], i+1, 100, 0, str(link), berry['x'], berry['y']/imHeight*height, -1, berry['half'])
=======
                        #print "Berry {} minx: {} maxx: {} x : {} \nminy: {} maxy: {} y : {} \n".format(min(pointA[0], pointB[0]), max(pointA[0], pointB[0]), berry['x'], min(pointA[1], pointB[1]),  max(pointA[1], pointB[1]), berry['y'] )
                        
                        if (pointA[0] < berry['y'] < pointB[0] and pointA[1] < berry['x'] < pointB[1]):
                            res = {'classID' : classID, 'x' : int((pointA[1] + pointB[1]) / 2), 'y' : int((pointA[0] + pointB[0]) / 2)}
                            # res = {'classID' : classID, 'x' : berry['x'], 'y' : berry['y']}
                            print "yep{}".format(index)
>>>>>>> e1b8e6c46df699a238b1a95f3208465efbf19638:new_main_old.py

                print "created not berry"
        state = 3
    if state == 3:
        while(state != 4):
                global delivering, collected

<<<<<<< HEAD:new_main.py
                size = len(ref.get())
                arr = ref.get()
                stats = []
                new_stats = []
                for i in range(1, size):
                    stats.append(ref.child(str(i)).child('status').get())
                isc = False
                while True:
                    new_stats[:] = []
                    ref = db.reference('/berrys')
                    for i in range(1, size):
                            new_stats.append(ref.child(str(i)).child('status').get())
                    print("new status", new_stats)
                    dif = len(new_stats) - len(stats)
                    for i in range(dif):
                        stats.append('')

                    for i in range(len(new_stats)):
                        if not(int(new_stats[i]) == int(stats[i])):
                            #print("Found difference")
                            changed_id.append(i + 1)
                            changed_stats.append(new_stats[i])
                            isc = True
                    if isc ==  True:
                        stats = list(new_stats)
                        # print(changed_id)
                        # print(changed_stats)
                        for i in range(len(changed_stats)):
                            if changed_stats[i] == '1':
                                q.append(changed_id[i])
                                del changed_id[i]
                                del changed_stats[i]
                                if not delivering : 
=======
                cv2.imwrite("../neurooutput/image{}.png".format(i), frame)

                os.remove("../photos/classes.out")
                
                if res is not None:

                    # uploaded_image = im.upload_image("../photos/img{}.png".format(i), title="Strawberry {}".format(i))
                    
                    link = 'https://i.imgur.com/CQdaHBw.png'

                    # print(uploaded_image.link)
                    create_new(ref, -berry['enc'], i+1, 100, 0, str(link), res['x'], res['y']/imHeight*height, res['classID'], berry['half'])

                    print "created"
                    # create_new(ref, -berry['enc'], i+1, 100, 0, str(uploaded_image.link), int(berry['x']), berry['y']/imHeight*height)
                else :
                    link = 'https://i.imgur.com/CQdaHBw.png'
                    notBerryCount += 1
                    # print(uploaded_image.link)
                    create_new(ref, -berry['enc'], i+1, 100, 0, str(link), berry['x'], berry['y']/imHeight*height, -1, berry['half'])

                    print "created not berry"
            state = 3
            size = len(ref.get())
            arr = ref.get()
            stats = []
            new_stats = []
            for i in range(1, size):
                stats.append(ref.child(str(i)).child('status').get())
            isc = False
        if state == 3:
            while(state != 4):
                if cv2.waitKey(1) == ord('u'):
                    send(7)
                    if wireless.current() != 'TELLO-AA1A76':
                        wireless.connect(ssid = 'TELLO-AA1A76', password = '')
                    state = 5
                    break
                new_stats[:] = []
                ref = db.reference('/berrys')
                for i in range(1, size):
                        new_stats.append(ref.child(str(i)).child('status').get())
                print("new status", new_stats)
                dif = len(new_stats) - len(stats)
                for i in range(dif):
                    stats.append('')

                for i in range(len(new_stats)):
                    if not(stats[i] != None and new_stats[i] != None and int(new_stats[i]) == int(stats[i])):
                        #print("Found difference")
                        changed_id.append(i + 1)
                        changed_stats.append(new_stats[i])
                        isc = True
                if isc ==  True:
                    stats = list(new_stats)
                    # print(changed_id)
                    # print(changed_stats)
                    for i in range(len(changed_stats)):
                        if changed_stats[i] == '1':
                            q.append(changed_id[i])
                            del changed_id[i]
                            del changed_stats[i]
                            if not delivering : 
                                state = 4
                                delivering = True
                        elif changed_stats[i] == '2':
                            q.remove(changed_id[i])
                            del changed_id[i]
                            del changed_stats[i]
                            if delivering : 
                                delivering = False
                                collected+=1
                                if collected == len(allberries) : close()
                                if len(q) > 0 :
                                    delivering = True
>>>>>>> e1b8e6c46df699a238b1a95f3208465efbf19638:new_main_old.py
                                    state = 4
                                    delivering = True
                            elif changed_stats[i] == '2':
                                q.remove(changed_id[i])
                                del changed_id[i]
                                del changed_stats[i]
                                if delivering : 
                                    delivering = False
                                    collected+=1
                                    if collected == len(allberries) : close()
                                    if len(q) > 0 :
                                        delivering = True
                                        state = 4
                                        
                        isc = False
                        print(q)
    if state == 4:
        currentBerry = q[0] - 1
        print(currentBerry)
        berry = allberries[currentBerry]

        print(berry)

        send(1, berry['x'], berry['y'], berry['enc'], berry['half'])
        while not readyToDeliver:
            time.sleep(0.003)
        
        print ("Trying")

<<<<<<< HEAD:new_main.py
        while True:
                        
            mask = cv2.inRange(hsv, low1, high1)
            mask += cv2.inRange(hsv, low2, high2)    
            cv2.bitwise_and(hsv, hsv, mask = mask)
            connectivity = 7
            output = cv2.connectedComponentsWithStats(mask, connectivity, cv2.CV_32S)
            num_labels = output[0]
            labels = output[1]
            stats = output[2]
            centroids = output[3]
            print(frame)
            picked = True

            cv2.imshow("image", frame)

            print(num_labels)

            if(num_labels > 0):
                for j in range(num_labels):
                    x, y, w, h, s = stats[j]
                    print("square{}".format(s))
                    if s > 2500 and s < 50000:
                        print((centroids[j][1] - berry['x'])**2 + (centroids[j][0] - berry['y'])**2)
                        if (centroids[j][1] - berry['x'])**2 + (centroids[j][0] - berry['y'])**2 < 5000:

                            send(5, centroids[j][1], centroids[j][0], berry['enc'], berry['half'])
                            picked = False      
            if picked:
                send(6)    
                break
            print ("Retrying")
        while delivering:
            time.sleep(0.003)
        del q[0]
        state = 3 
    if state == 5:
        drone = tellopy.Tello()
        drone.subscribe(drone.EVENT_FLIGHT_DATA, tello_handler)
        drone.connect()
        while drone.connected:
            key = getkey()
            if key == 'u':
                drone.takeoff()
                drone.down(60)
                drone.right(15)
                sleep(4)
                drone.down(0)
                drone.right(0)
                sleep(1)
                drone.down(40)
                sleep(3)
                drone.down(0)
                sleep(2)
                drone.forward(20)
                sleep(3)
                drone.forward(0)
                sleep(1)
                drone.right(20)
                sleep(4)
                drone.right(0)
                sleep(3)
                drone.down(50)
                drone.land()
                sleep(5)
                drone.quit()
                break
        state == 6
=======
            send(1, berry['x'], berry['y'], berry['enc'], berry['half'])
            
            print ("Trying")

            cap = cv2.VideoCapture(cameraId)
            
            while True:    

                while not readyToDeliver:
                    time.sleep(0.003)
                
                readyToDeliver = False

                cap_read_retries = 0

                while cap_read_retries < 5:        
                    ret, frame = cap.read()
                    
                    time.sleep(0.01)
                    cap_read_retries+=1

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                mask = cv2.inRange(hsv, low1, high1)
                mask += cv2.inRange(hsv, low2, high2)    
                cv2.bitwise_and(hsv, hsv, mask = mask)
                connectivity = 7
                output = cv2.connectedComponentsWithStats(mask, connectivity, cv2.CV_32S)
                num_labels = output[0]
                labels = output[1]
                image_stats = output[2]
                centroids = output[3]

                picked = True

                print(num_labels)

                if(num_labels > 0):
                    for j in range(num_labels):
                        x, y, w, h, s = image_stats[j]
                        print("square{}".format(s))
                        if s > 2500 and s < 50000:
                            print((centroids[j][1] - berry['x'])**2 + (centroids[j][0] - berry['y'])**2)
                            if (centroids[j][1] - berry['x'])**2 + (centroids[j][0] - berry['y'])**2 < 10000:

                                send(5, centroids[j][1], centroids[j][0], berry['enc'], berry['half'])
                                picked = False      
                if picked:
                    send(6)  
                    cap.release()  
                    break
                print ("Retrying")
            while delivering:
                time.sleep(0.003)
            del q[0]
#             send(7)
#             if wireless.current() != 'TELLO-AA1A76':
#                 wireless.connect(ssid = 'TELLO-AA1A76', password = '')
#             state = 5
            state = 3 
        if state == 5:
            print('Waiting for drone...')
            # while not readyToFly:
            #     sleep(0.03)
            # while drone.connected:
            #     drone.takeoff()
            #     drone.down(60)
            #     drone.right(15)
            #     sleep(4)
            #     drone.down(0)
            #     drone.right(0)
            #     sleep(1)
            #     drone.down(30)
            #     sleep(3)
            #     drone.down(0)
            #     sleep(2)
            #     drone.forward(30)
            #     sleep(3)
            #     drone.forward(0)
            #     sleep(1)
            #     drone.right(20)
            #     sleep(2)
            #     drone.right(0)
            #     sleep(3)
            #     drone.down(50)
            #     drone.land()
            #     sleep(5)
            #     drone.quit()
            #     break
            print("Finished")
            state == 6
    except BaseException as e:
        traceback.print_exc()
        cap.release()
        conn.close()
        exit()
>>>>>>> e1b8e6c46df699a238b1a95f3208465efbf19638:new_main_old.py

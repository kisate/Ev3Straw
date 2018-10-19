from cv2 import cv2 
import numpy as npy
import socket 
from time import sleep
import threading
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pyimgur

host = '192.168.1.4'
port = 51000 # random number
a = True

q = []

changed_id = []
changed_stats = []
CLIENT_ID = "733b83d64f87370"

endPos = 5000

first = -1

collected = 0 
delivering = False

pos = 0
cap = cv2.VideoCapture(1)

cv2.namedWindow('image')

low1 = npy.array([0, 130, 90])
high1 = npy.array([15, 255, 255])
low2 = npy.array([165, 130, 90])
high2 = npy.array([180, 255, 255])

low3 = npy.array([69, 100, 120])
high3 = npy.array([75, 200, 220])

berries = [[],[]]
allberries = []

switch = 0
lastid = -1

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try : 
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

except Exception:
    pass

s.bind(('', 51000))
s.listen(5)

def initialize():
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://strawberryfinder.firebaseio.com/',
        'databaseAuthVariableOverride': {
            'uid': 'firebase-adminsdk-z6zvt@strawberryfinder.iam.gserviceaccount.com'
        }
    })
    return db.reference('/berrys')


def create_new(ref, enc, n, price, status, url,  x, y):
    ref.child(str(n)).set({
        'encoder' : enc,
        'id' : n,
        'price' : price,
        'status' : str(status),
        'url' : url,
        'x' : x,
        'y' : y
    })    

def update_status(ref, n, status):
    ref.child(str(n)).update({
        'status': str(status),
    })


def check(ref):
    #while True:

    global delivering, collected

    size = len(ref.get())
    arr = ref.get()
    stats = []
    new_stats = []
    for i in range(1, size):
        stats.append(ref.child(str(i)).child('status').get())
    #print(stats)
    isc = False
    while True:
        new_stats.clear()
        ref = db.reference('/berrys')
        for i in range(1, size):
                new_stats.append(ref.child(str(i)).child('status').get())
        #print("new status", new_stats)
        dif = len(new_stats) - len(stats)
        for i in range(dif):
            stats.append('')
        #print(stats)

        for i in range(len(new_stats)):
            #print("stats i el:", stats[i], "new stats i el", new_stats[i]) 
            if not(int(new_stats[i]) == int(stats[i])):
                #print("Found difference")
                changed_id.append(i + 1)
                changed_stats.append(new_stats[i])
                isc = True
        # print(stats, new_stats, isc)
        # print("------------------") 
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
                        threading.Thread(target=deliver, args=(q[0]-1,)).start()
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
                            threading.Thread(target=deliver, args=(q[0]-1,)).start()
                            
            isc = False
            print(q)
    return 

def deliver(i):

    berry = allberries[i]

    send(1, berry['x'], berry['y'], berry['pos'])

    while delivering:
        time.sleep(0.003)

def handleMessage(message):
    global pos, delivering
    if message[0] == 1:
        pos = message[1]
    if message[0] == 2:
        delivering = False

def reader():
    global conn
    
    while a:
        message = []

        part = conn.recv(1)
        
        message_size = int.from_bytes(part, byteorder='big')

        for i in range(message_size):
            part = conn.recv(8)
            message.append(int.from_bytes(part, byteorder='big'))

        handleMessage(message)
        if len(part) == 0 : break

def send(*args):
        
    msg = len(args).to_bytes(1, byteorder='big')

    for a in args:
        msg += (int(a)).to_bytes(8, byteorder='big')

    conn.send(msg)

def draw_circle(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        send(1, y, x, 3000)

conn, addr = s.accept()

print(addr)

threading.Thread(target=reader, args=()).start()

send(3, endPos)

while(pos < endPos):
    # Capture frame-by-frame    
    ret, frame = cap.read()
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
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

                allberries.append({'x' : centroids[i][1], 'y' : centroids[i][0], 'id' : lastid, 'enc' : pos, 'frame' : frame[max(int(centroids[i][1] - 200), 0):int(centroids[i][1])+200, max(int(centroids[i][0]) - 200, 0):int(centroids[i][0])+200]})
                #allberries.append({'x' : centroids[i][0], 'y' : centroids[i][1], 'id' : lastid, 'enc' : 311})
            else :
                berries[(switch + 1)%2].append({'x' : centroids[i][0], 'y' : centroids[i][1], 'id' : b})

    print(pos)
    switch=(switch + 1)%2
    cv2.imshow('image', frame)
    
    if cv2.waitKey(1)  == ord('q'):
        cap.release()
        cv2.destroyAllWindows()  
        exit()

cap.release()
cv2.destroyAllWindows()    
ref = initialize()
im = pyimgur.Imgur(CLIENT_ID)

db.reference('/berrys').delete()
for i, berry in enumerate(allberries):
    cv2.imwrite( "./img{}.png".format(i), berry['frame'])
    uploaded_image = im.upload_image("./img{}.png".format(i), title="Strawberry {}".format(i))
    print(uploaded_image.link)
    create_new(ref, berry['enc'], i+1, 100, 0, str(uploaded_image.link), int(berry['x']), berry['y']/imHeight*height)

thread1 = threading.Thread(target=check, args=(ref,))
thread1.start()  


print('fin')
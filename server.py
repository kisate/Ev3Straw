import socket, threading

import sys

sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')

import cv2.cv2

host = '192.168.1.4'
port = 51000 # random number
a = True



def reader():
    
    global conn
    
    while a:

        message = []

        part = conn.recv(1)
        
        message_size = int.from_bytes(part, byteorder='big')

        for i in range(message_size):
            part = conn.recv(8)
            message.append(int.from_bytes(part, byteorder='big', signed=True))

        print (message)
        if len(part) == 0 : break

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try : 
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
except Exception:
    pass
s.bind(('', 51000))

s.listen(5)

def send(*args):
        
    msg = len(args).to_bytes(1, byteorder='big')

    for a in args:
        msg += (int(a)).to_bytes(8, byteorder='big', signed=True)

    conn.send(msg)

def inputer():
    line = input()

    while line != '0':
        send(*line.split())
        line = input()
    


def draw_circle(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        send(1, y, x, 3000)
    
cv2.namedWindow('frame')    
cv2.setMouseCallback('frame', draw_circle)
cap = cv2.VideoCapture(1)

conn, addr = s.accept()

print(addr)

threading.Thread(target=reader, args=()).start()

threading.Thread(target=inputer, args=()).start()

count = 15

while True:
        _, frame = cap.read()

        cv2.imshow('frame', frame)

        key = cv2.waitKey(1)

        if key == ord('q'):
            cv2.destroyAllWindows()
            break
        if key == ord('a'):
            cv2.imwrite('/home/forester/Documents/klubnikor/eval/{:03d}.png'.format(count), frame)
            count+=1

a = False

s.close()
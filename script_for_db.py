
import firebase_admin
import base64
from firebase_admin import credentials
from firebase_admin import db
import binascii
import cv2

CLIENT_ID = "733b83d64f87370"

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

def setPic(ref, n, pic):
    ref.child(str(n)).child('pic').set(
        base64.encodestring(pic).decode('ascii'))    


retval, buffer = cv2.imencode('.png', cv2.imread('e000.png'))

print(bytearray(buffer))

ref = initialize()

for i in range(1, 11):
    setPic(ref, i, bytearray(buffer))

for i in range(1, 11):
    pic = binascii.a2b_base64(ref.child(str(i)).child('pic').get())
    f = open('test{}.png'.format(i), 'wb')
    f.write(pic)
    f.close()



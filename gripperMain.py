#!/usr/bin/env python3
import smbus, threading
from threading import Thread

import time

from math import acos, pi

from ev3dev2.motor import LargeMotor, OUTPUT_B, SpeedPercent, MoveTank, OUTPUT_A, OUTPUT_C, MediumMotor, OUTPUT_D
from ev3dev2.sensor import INPUT_2
from ev3dev2.sensor.lego import TouchSensor

from ev3socketclient import Client

servoAddresses = [0x42, 0x43, 0x44, 0x45, 0x46, 0x47]

imWidth = 480
imHeight = 640

width = 19
height = 26

length = 19

downAngle = 52
upAngle = 20
defaultAngle = 160
defaultAngle2 = 20

cameraEnc = 1800

encToCm = 4.1/360

deltaX1 = -2    
deltaY1 = -4

deltaX2 = -2
deltaY2 = -5

udServo = 0
lrServo = 5

lastMessage = []

host = '192.168.1.3'
port = 51004 # fig number

# code goes here ---------------

servo = smbus.SMBus(3) # input port 1 
servo.write_i2c_block_data(0x01, 0x48, [0xAA]) # xAA - disable 10 second timeout / xFF - no servo control / x00 - 10 second timeout

moving_motor = LargeMotor(OUTPUT_A)
pump_motor = LargeMotor(OUTPUT_B)
camera_motor = MediumMotor(OUTPUT_C)
drone_motor = LargeMotor(OUTPUT_D)

touch = TouchSensor(INPUT_2)

client = Client(host, port)

def moveDroneToStartPos():

    drone_motor.on(SpeedPercent(-40))
    while (drone_motor.position > -1300):
        print(drone_motor.position)
        time.sleep(0.003)
 
    drone_motor.stop()

def moveDroneToGetPos():

    drone_motor.on(SpeedPercent(40))
    while (drone_motor.position < 550):
        print(drone_motor.position)
        time.sleep(0.003)
 
    drone_motor.stop()

def getServoPos(channel_id):
    return servo.read_i2c_block_data(0x01, servoAddresses[channel_id])[0]

def setServoPos(channel_id, position):
    servo.write_i2c_block_data(0x01, servoAddresses[channel_id], [position % 256])

def rotateServo(channel_id, position, step = 0.05):

    position %= 256

    current = getServoPos(channel_id)
    
    print("{} {}".format(current, position))
    
    while (current < position):            
        current = min(position, current + 2)
        setServoPos(channel_id, current)

        time.sleep(step)

    while (current > position):
        current = max(position, current - 2)
        setServoPos(channel_id, current)

        time.sleep(step)

def rotateServoOnDefault() :
    rotateServo(lrServo, defaultAngle)
    rotateServo(udServo, upAngle)

class StopThread(StopIteration):
    pass

class SupportThread(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name
        self.exit = threading.Event()
    
    def run(self) :           
        while not self.exit.is_set():
            pump_motor.on(SpeedPercent(100))
            self.exit.wait(0.1)
            pump_motor.reset()
            self.exit.wait(1.2)
        
        pump_motor.reset()

            
    def stop(self) :
        self.exit.set()

support_thread = SupportThread('support')

def deliver():
    getToPickPosition(178, 41, -10953, 2)
    '''
    target = -10000

    moving_motor.on(SpeedPercent(-100))
    
    while (moving_motor.position > target - 953):
        client.send(1, moving_motor.position)

    moving_motor.stop()
    '''

    rotateServo(udServo, downAngle - 20)
    
    support_thread.stop()

    pump_motor.on(SpeedPercent(-100))
    time.sleep(2)

    rotateServo(udServo, upAngle - 10)

    pump_motor.reset()

    client.send(2)

def deliverToDrone():
    
    target = -10955
    x = 130
    y = 110

    rotateServo(lrServo, upAngle)

    rotateServo(lrServo, defaultAngle, 0.05)
    
    rotateServo(udServo, upAngle - 20)
    
    rideToEnc(target)
    
    moving_motor.stop()

    dx = (imWidth - x)/imWidth*width + deltaX2
    dy = -((imHeight - y)/imHeight*height + deltaY2)
    
    r = ((length)*(length) - dy*dy)**0.5

    if (r > dx) :
        distanceToGo = r - dx
        start = moving_motor.position
        moving_motor.on(SpeedPercent(20))

        while (moving_motor.position - start < int(distanceToGo/encToCm)) : 
            time.sleep(0.003)
    

    elif (r < dx) :
        distanceToGo = dx - r
        start = moving_motor.position
        moving_motor.on(SpeedPercent(-20))

        while (start - moving_motor.position < int(distanceToGo/encToCm)) : 
            time.sleep(0.003)
    
    moving_motor.stop()

    angle = getRotAngle(dy)

    print(angle)

    rotateServo(lrServo, angle)


    rotateServo(udServo, downAngle - 35)

    client.send(2)
    
    support_thread.stop()

    pump_motor.on(SpeedPercent(-100))

    time.sleep(5)

    pump_motor.reset()

    rotateServo(udServo, upAngle-20)
    rideToEnc(-9000)

    
def pick():

    global support_thread

    pump_motor.on(SpeedPercent(-100))

    rotateServo(udServo, downAngle, 0.03)

    pump_motor.reset()

    time.sleep(1)

    pump_motor.on(SpeedPercent(100))

    time.sleep(1)

    pump_motor.reset()

    time.sleep(1)

    rotateServo(udServo, upAngle - 10, 0.08)

    support_thread = SupportThread('support')

    #time.sleep(2)

    rotateServo(udServo, upAngle)
    
    support_thread.start()

    #support_thread.stop()

def getRotAngle(dy):
    sinA = dy/length
    return max (0, (int)(256*acos(sinA)/pi) - 30)

def rideToEnc(enc, percent = 100):
    position = moving_motor.position

    print ("Riding to {}".format(enc))

    if position < enc:
        moving_motor.on(SpeedPercent(percent))
        while moving_motor.position < enc:
            time.sleep(0.001)
            #print(moving_motor.position)
            client.send(1, moving_motor.position)
        moving_motor.stop()
    elif position > enc:
        moving_motor.on(SpeedPercent(-percent))
        while moving_motor.position > enc:
            time.sleep(0.001)
            #print(moving_motor.position)
            client.send(1, moving_motor.position)
        moving_motor.stop()
                

def getToRotatingPosition(dx, dy):
    print (dy)
    r = (length*length - dy*dy)**0.5

    if (r > dx) :
        distanceToGo = r - dx
        start = moving_motor.position
        moving_motor.on(SpeedPercent(20))

        while (moving_motor.position - start < int(distanceToGo/encToCm)) : 
            time.sleep(0.003)
    

    elif (r < dx) :
        distanceToGo = dx - r
        start = moving_motor.position
        moving_motor.on(SpeedPercent(-20))

        while (start - moving_motor.position < int(distanceToGo/encToCm)) : 
            time.sleep(0.003)
    
    moving_motor.stop()

def getToPickPosition(x, y, pos, half):
    rotateServo(udServo, upAngle)
    if (half == 2 ) : rotateServo(lrServo, defaultAngle, 0.05)
    else : rotateServo(lrServo, defaultAngle2, 0.05)
    rotateServo(udServo, upAngle)
    
    print (pos)

    rideToEnc(pos)
    
    moving_motor.stop()


    if (half == 1):
        dx = (imWidth - x)/imWidth*width + deltaX1
        dy = y/imHeight*height + deltaY1

    else:
        dx = (imWidth - x)/imWidth*width + deltaX2
        dy = -((imHeight - y)/imHeight*height + deltaY2)


    getToRotatingPosition(dx, dy)

    moveCameraToPosition(half)

    angle = getRotAngle(dy)

    print(angle)

    rotateServo(udServo, upAngle)

    rotateServo(lrServo, angle)



def collect(_x, _y, _pos, _half):
    
    picked = False

    x, y, pos, half = _x, _y, _pos, _half

    while True:

        rotateServo(udServo, upAngle)

        getToPickPosition(x, y, pos, half)

        time.sleep(2)

        pick()

        rotateServo(udServo, upAngle)

        if (half == 1 ) : rotateServo(lrServo, defaultAngle, 0.05)
        else : rotateServo(lrServo, defaultAngle2, 0.05)
        rotateServo(udServo, upAngle - 10)
        print("Half is ", half)
    
        rideToEnc(pos, 20)

        client.send(4)

        print ("Waiting for response")

        while (messagehandler.state == 0):
            time.sleep(0.001)

        if (messagehandler.state == 5):
            message = messagehandler.message
            x, y, pos, half = message[1], message[2], message[3], message[4]
            messagehandler.state = 0
            support_thread.stop()
            pump_motor.on(SpeedPercent(-100))
            time.sleep(0.8)
            pump_motor.reset()
            print ("Not picked")

        elif (messagehandler.state == 6):
            messagehandler.state = 0
            picked = True
            print ("Picked")

        if picked :
            break
    
    deliverToDrone()
    

def calibrate():
    moving_motor.on(SpeedPercent(100))
    while not touch.is_pressed:
        time.sleep(0.003)
    moving_motor.stop()

    moving_motor.position = 0
    camera_motor.position = 0
    drone_motor.position = 0

def returnPlatform():
    drone_motor.on(SpeedPercent(40))
    while (drone_motor.position < 0):
        time.sleep(0.003) 

    drone_motor.stop()

def finish():
    global support_thread
    support_thread.stop()
    moving_motor.reset()
    pump_motor.reset()
    
    moveCameraToPosition(1)
    
    returnPlatform()

    camera_motor.reset()
    drone_motor
    client.disconnect()
    servo.write_i2c_block_data(0x01, 0x48, [0xFF])

def moveCameraToPosition(pos):

    if (pos == 1):
        print("Move camera to start")
        camera_motor.on(SpeedPercent(-20))
        while (camera_motor.position > 0):
            time.sleep(0.003) 
    else:
        print("Move camera to ", cameraEnc)
        camera_motor.on(SpeedPercent(20))
        while (camera_motor.position < cameraEnc):
            time.sleep(0.003)
    
    camera_motor.stop()

class MessageHandler():
    def __init__(self):
        self.state = 0
        self.message = []
    
    def updateMessage(self, message):
        self.message = message
        self.state = message[0]
        print("in handler : " + str(message) + " " + str(self.state))

messagehandler = MessageHandler()

def waitForCommand():

    while True:
        try :
            if (messagehandler.state == 0):
                time.sleep(0.005)

            if (messagehandler.state == 1):
                message = messagehandler.message
                print(message)
                messagehandler.state = 0
                
                collect(message[1], message[2], message[3], message[4])
            if (messagehandler.state == 2):
                message = messagehandler.message
                print(message)
                messagehandler.state = 0
                
                rotateServo(udServo, message[1])
                rotateServo(lrServo, message[2])
            if (messagehandler.state == 3):
                message = messagehandler.message
                print(message)
                messagehandler.state = 0

                target = message[1] - 50

                position = moving_motor.position
                if position < target:
                    moving_motor.on(SpeedPercent(80))
                    while moving_motor.position < target:
                        time.sleep(0.001)
                        #print(-moving_motor.position)
                        client.send(1, moving_motor.position)
                    moving_motor.stop()
                elif position > target:
                    moving_motor.on(SpeedPercent(-80))
                    while moving_motor.position > target:
                        time.sleep(0.001)
                        print(moving_motor.position)
                        client.send(1, moving_motor.position)
                    moving_motor.stop()
                if (messagehandler.state == 4):
                    message = messagehandler.message
                    print(message)
                    messagehandler.state = 0

                    moveCameraToPosition(2)
                    rotateServo(udServo, upAngle)
                    rotateServo(lrServo, defaultAngle2)

                    client.send(3)

                    time.sleep(1)

                    target = 0

                    position = moving_motor.position
                    if position < target:
                        moving_motor.on(SpeedPercent(80))
                        while moving_motor.position < target:
                            time.sleep(0.001)
                            #print(-moving_motor.position)
                            client.send(1, moving_motor.position)
                        moving_motor.stop()
                    elif position > target:
                        moving_motor.on(SpeedPercent(-80))
                        while moving_motor.position > target:
                            time.sleep(0.001)
                            print(moving_motor.position)
                            client.send(1, moving_motor.position)
                        moving_motor.stop()
            if (messagehandler.state == 7):
                print("Ready")
                messagehandler.state = 0

                drone_motor.on(SpeedPercent(-40))
                while (drone_motor.position > -1800):
                    print(drone_motor.position)
                    time.sleep(0.003)
                drone_motor.stop()
                client.send(5)

        except BaseException as e:
            finish()
            print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print (e)
            break
setServoPos(udServo, upAngle)
setServoPos(lrServo, defaultAngle)

#rotateServoOnDefault()
time.sleep(5)

calibrate()

moving_motor.stop()

print("connecting")

client.connect(messagehandler)

print("connected")

time.sleep(0.2)

waitForCommand()

# drone_motor.on(SpeedPercent(-100))

# time.sleep(0.3)

# drone_motor.reset()

finish()
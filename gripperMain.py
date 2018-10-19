#!/usr/bin/env python3
import smbus, threading
from threading import Thread

import time

from math import acos, pi

from ev3dev2.motor import LargeMotor, OUTPUT_A, SpeedPercent, MoveTank, OUTPUT_D
from ev3dev2.sensor import INPUT_2
from ev3dev2.sensor.lego import TouchSensor

from ev3socketclient import Client

servoAddresses = [0x42, 0x43, 0x44, 0x45, 0x46, 0x47]

imWidth = 480
imHeight = 640

width = 17.3
height = 23.3

length = 19

downAngle = 40
upAngle = 5
defaultAngle = 130

encToCm = 4.1/360

deltaX = -3
deltaY = -5

udServo = 0
lrServo = 5

lastMessage = []

host = '192.168.1.3'
port = 51000 # random number

# code goes here ---------------

servo = smbus.SMBus(3) # input port 1 
servo.write_i2c_block_data(0x01, 0x48, [0xAA]) # xAA - disable 10 second timeout / xFF - no servo control / x00 - 10 second timeout

moving_motor = LargeMotor(OUTPUT_A)
pump_motor = LargeMotor(OUTPUT_D) # Should be D

touch = TouchSensor(INPUT_2)

client = Client(host, port)

def getServoPos(channel_id):

    return servo.read_i2c_block_data(0x01, servoAddresses[channel_id])[0]

def setServoPos(channel_id, position):
    servo.write_i2c_block_data(0x01, servoAddresses[channel_id], [position % 256])

def rotateServo(channel_id, position):

    position %= 256

    current = getServoPos(channel_id)
    
    print("{} {}".format(current, position))
    
    while (current < position):            
        current = min(position, current + 2)
        setServoPos(channel_id, current)

        time.sleep(0.01)

    while (current > position):
        current = max(position, current - 2)
        setServoPos(channel_id, current)

        time.sleep(0.01)

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
            self.exit.wait(0.4)
            pump_motor.stop()
            self.exit.wait(0.14)
        
        pump_motor.stop()

            
    def stop(self) :
        self.exit.set()

support_thread = SupportThread('support')

def deliver():
    target = -4000

    rotateServoOnDefault()

    moving_motor.on(SpeedPercent(-60))
    
    while (moving_motor.position > target):
        client.send(1, -moving_motor.position)

    moving_motor.stop()
    
    rotateServo(udServo, downAngle - 20)

    client.send(2, 0)

    support_thread.stop()

def pick():

    global support_thread

    pump_motor.on(SpeedPercent(-100))
    time.sleep(1.3)

    rotateServo(udServo, downAngle)

    pump_motor.on(SpeedPercent(100))

    time.sleep(1)

    support_thread = SupportThread('support')
    support_thread.start()

    time.sleep(2)

    rotateServo(udServo, upAngle)

    #support_thread.stop()

def getRotAngle(dy):
    sinA = dy/length
    return max (0, (int)(256*acos(sinA)/pi) - 30)

def getToRotatingPosition(dx, dy):
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

def collect(x, y, pos):
    rotateServo(lrServo, defaultAngle)
    delta = moving_motor.position - pos

    if delta > 0 :

        moving_motor.on(SpeedPercent(-80))

        while(moving_motor.position > pos):
            time.sleep(0.003)

    else : 

        moving_motor.on(SpeedPercent(80))

        while(moving_motor.position < pos):
            time.sleep(0.003)
    
    moving_motor.stop()

    dx = (imWidth - x)/imWidth*width + deltaX
    dy = y/imHeight*height + deltaY

    getToRotatingPosition(dx, dy)

    angle = getRotAngle(dy)

    print(angle)

    rotateServo(lrServo, angle)

    time.sleep(2)
        
    pick()

    deliver()

    support_thread.stop()

def calibrate():
    moving_motor.on(SpeedPercent(80))
    while not touch.is_pressed:
        time.sleep(0.003)
    moving_motor.stop()

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
        if (messagehandler.state == 0):
            time.sleep(0.005)
      
        if (messagehandler.state == 1):
            message = messagehandler.message
            print(message)
            messagehandler.state = 0
            
            collect(message[1], message[2], -message[3])
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

            position = -moving_motor.position
            if position > message[1]:
                moving_motor.on(SpeedPercent(60))
                while -moving_motor.position > message[1]:
                    time.sleep(0.003)
                moving_motor.stop()
            elif position < message[1]:
                moving_motor.on(SpeedPercent(-60))
                while -moving_motor.position < message[1]:
                    time.sleep(0.003)
                moving_motor.stop()
            
calibrate()


client.connect(messagehandler)



waitForCommand()

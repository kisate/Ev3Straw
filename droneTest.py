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

udServo = 0
lrServo = 5

servo = smbus.SMBus(3) # input port 1 
servo.write_i2c_block_data(0x01, 0x48, [0xAA]) # xAA - disable 10 second timeout / xFF - no servo control / x00 - 10 second timeout


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
    rotateServo(lrServo, 0)
    rotateServo(udServo, 0)

#rotateServo(udServo, 20)
rotateServo(lrServo, 0)
#time.sleep(1)
#rotateServo(udServo, 60)
#rotateServo(lrServo, 180)
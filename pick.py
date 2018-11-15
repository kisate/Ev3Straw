#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_B, SpeedPercent, MoveTank
import time
import smbus
# TODO: Add code here

servoAddresses = [0x42, 0x43, 0x44, 0x45, 0x46, 0x47]

downAngle = 52
upAngle = 10
defaultAngle = 130

udServo = 0
lrServo = 5

# code goes here ---------------

servo = smbus.SMBus(3) # input port 1 
servo.write_i2c_block_data(0x01, 0x48, [0x00]) # xAA - disable 10 second timeout / xFF - no servo control / x00 - 10 second timeout

def getServoPos(channel_id):

    return servo.read_i2c_block_data(0x01, servoAddresses[channel_id])[0]

def setServoPos(channel_id, position):
    servo.write_i2c_block_data(0x01, servoAddresses[channel_id], [position % 256])

def rotateServo(channel_id, position, step = 0.1):

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

m = LargeMotor(OUTPUT_B)


setServoPos(lrServo, 50)
setServoPos(udServo, upAngle)

rotateServo(lrServo, 50)

rotateServo(udServo, upAngle)

m.on(SpeedPercent(-100))


rotateServo(udServo, downAngle, 0.03)

m.reset()

time.sleep(1)

m.on(SpeedPercent(100))

time.sleep(1.4)

m.reset()

rotateServo(udServo, upAngle - 10, 0.08)

counter = 0

try :

    while True:
        m.on(SpeedPercent(100))
        time.sleep(0.15)    
        m.reset()
        time.sleep(0.8)
       
        counter+=1
        # if counter == 5:
        #     rotateServo(udServo, downAngle-10)
            
except KeyboardInterrupt:
    m.reset()

    
#!/usr/bin/env python3
import smbus
import time
from ev3dev2.motor import LargeMotor, OUTPUT_A, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor

# HiTechnic doc http://www.hitechnic.com/blog/wp-content/uploads/HiTechnic-Servo-Controller-Specification.pdf

servo = smbus.SMBus(3) # input port 1

servo.write_i2c_block_data(0x01, 0x48, [0xAA]) # xAA - disable 10 second timeout / xFF - no servo control / x00 - 10 second timeout
servo.write_i2c_block_data(0x01, 0x42, [0]) # channel 1 
servo.write_i2c_block_data(0x01, 0x43, [0]) # channel 2 
time.sleep(0.3)

a = 0

while a < 1:
    servo.write_i2c_block_data(0x01, 0x42, [250])
    servo.write_i2c_block_data(0x01, 0x43, [0])
    time.sleep(0.2)
    servo.write_i2c_block_data(0x01, 0x43, [120])
    time.sleep(0.2)
    servo.write_i2c_block_data(0x01, 0x42, [0])
    servo.write_i2c_block_data(0x01, 0x43, [250])
    time.sleep(0.2)
    servo.write_i2c_block_data(0x01, 0x43, [120])
    time.sleep(0.2)
    a+=1

servo.write_i2c_block_data(0x01, 0x42, [30])
servo.write_i2c_block_data(0x01, 0x43, [50])

servo.write_i2c_block_data(0x01, 0x44, [70])

servo.write_i2c_block_data(0x01, 0x45, [90])
servo.write_i2c_block_data(0x01, 0x46, [110])

servo.write_i2c_block_data(0x01, 0x47, [130])

print (servo.read_i2c_block_data(0x01, 0x42))
print (servo.read_i2c_block_data(0x01, 0x43))
print (servo.read_i2c_block_data(0x01, 0x44))
print (servo.read_i2c_block_data(0x01, 0x45))
print (servo.read_i2c_block_data(0x01, 0x46))
print (servo.read_i2c_block_data(0x01, 0x47))
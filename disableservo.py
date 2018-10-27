#!/usr/bin/env python3
import smbus
import time
from ev3dev2.motor import LargeMotor, OUTPUT_A, SpeedPercent, MoveTank
#from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor

# HiTechnic doc http://www.hitechnic.com/blog/wp-content/uploads/HiTechnic-Servo-Controller-Specification.pdf

servo = smbus.SMBus(3) # input port 1

servo.write_i2c_block_data(0x01, 0x48, [0xFF]) # xAA - disable 10 second timeout / xFF - no servo control / x00 - 10 second timeout

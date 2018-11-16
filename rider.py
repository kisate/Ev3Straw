#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_C, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_2
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds
import time

# TODO: Add code here

m = LargeMotor(OUTPUT_A)

line = input()

m.position = 0

while line != "stop":
    target = int(line)
    while m.position > target:
        m.on(SpeedPercent(-100))
    while m.position < target:
        m.on(SpeedPercent(100))
    
    m.stop()

    line = input()

m.reset()
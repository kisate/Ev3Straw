#!/usr/bin/env python3
from ev3dev2.motor import MediumMotor, OUTPUT_A, OUTPUT_C, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_2
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds
import time

# TODO: Add code here

m = MediumMotor(OUTPUT_C)

m.on(SpeedPercent(-20))

m.position = 0

while m.position > 0:
    time.sleep(0.03)

m.reset()
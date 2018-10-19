#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_2
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds

# TODO: Add code here

ts = TouchSensor(INPUT_2)

m = LargeMotor(OUTPUT_D)

while True:
    if ts.is_pressed:
        m.on(SpeedPercent(100))
    else:
        m.reset()

        
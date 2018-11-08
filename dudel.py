#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_B, SpeedPercent, MoveTank
import time
# TODO: Add code here

m = LargeMotor(OUTPUT_B)

m.on(SpeedPercent(-100))

time.sleep(2)

m.on(SpeedPercent(100))

time.sleep(1)

try :

    while True:
        m.reset()
        time.sleep(0.25)
        m.on(SpeedPercent(100))
        time.sleep(0.25)
except KeyboardInterrupt:
    m.reset()
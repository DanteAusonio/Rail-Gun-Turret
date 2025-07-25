import RPi.GPIO as GPIO, time
import pigpio

PAN_PIN = 13
TILT_PIN = 19


pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpiod!")


def set_pan(angle_deg):
    us = 500 + (angle_deg / 180.0) * 2000
    pi.set_servo_pulsewidth(TILT_PIN, us)


def set_tilt(angle_deg):
    us = 500 + (angle_deg / 180.0) * 2000
    pi.set_servo_pulsewidth(TILT_PIN, us)


for a in range(0, 181, 10):
    print("Moving Pan")
    set_pan(a)
    time.sleep(0.1)


pi.set_servo_pulsewidth(PAN_PIN, 0)
pi.stop()
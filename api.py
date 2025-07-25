from flask import Flask, request, jsonify, Response
import RPi.GPIO as GPIO
from stream_video import gen_frames
import time
import threading
from flask_socketio import SocketIO
import pigpio


# ------------------ Configuration ----------------------

pi = pigpio.pi()

# Pin MACROS
FIRE_PIN = 17
PAN_PIN = 13
TILT_PIN = 19

# Servo MACROS
MIN_DUTY = 2
MAX_DUTY = 12
STOP_DUTY = 7.5


PAN_MIN = 0
PAN_MAX = 100

TILT_MIN = 0
TILT_MAX = 100


pan_angle = 50
tilt_angle = 50
pan_dir   = None    # "left","right", or None
tilt_dir  = None    # "up","down", or None


# GPIO Set Up
GPIO.setmode(GPIO.BCM)

# Set up Fire Pin
# GPIO.setup(FIRE_PIN, GPIO.OUT)
# GPIO.output(FIRE_PIN, GPIO.HIGH)
pi.set_mode(FIRE_PIN, pigpio.OUTPUT)
pi.write(FIRE_PIN, 1)


# Set up Pan Servo
GPIO.setup(PAN_PIN, GPIO.OUT)
pan_pwm = GPIO.PWM(PAN_PIN, 50)
pan_pwm.start(STOP_DUTY)


# Set Up Tilt Servo
GPIO.setup(TILT_PIN, GPIO.OUT)
tilt_pwm = GPIO.PWM(TILT_PIN, 50)
tilt_pwm.start(STOP_DUTY)




app = Flask(__name__)
socketio = SocketIO(app)




@app.route('/fire', methods=['POST'])
def fire():
    # GPIO.output(FIRE_PIN, GPIO.LOW)
    # time.sleep(1)
    # GPIO.output(FIRE_PIN, GPIO.HIGH)
    pi.write(FIRE_PIN, 0)
    time.sleep(1)
    pi.write(FIRE_PIN, 1)
    time.sleep(0.05)
    
    pi.set_PWM_frequency(FIRE_PIN, 200)
    pi.set_PWM_dutycycle(FIRE_PIN, 128)
    
    return jsonify({'success' : True})



@app.route('/video_feed')
def video_feed():
    return Response(
        gen_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )











@app.route('/servo_control/<direction>', methods=['POST'])
def servo_control(direction):
    global pan_dir
    global tilt_dir
    if direction in ('left', 'right'):
        pan_dir = direction
    elif direction in ('up', 'down'):
        tilt_dir = direction
    elif direction == 'stop':
        pan_dir = None
        tilt_dir = None
    
    return jsonify(ok=True)







def angle_to_duty(a):
    return MIN_DUTY + (a/270)*(MAX_DUTY-MIN_DUTY)


def servo_loop():
    global pan_angle, tilt_angle
    servo_speed = 0.1
    while True:
        if pan_dir == 'right' and pan_angle < PAN_MAX:
            pan_angle += 1
            pan_pwm.ChangeDutyCycle(pan_angle)

        elif pan_dir == 'left' and pan_angle > PAN_MIN:
            pan_angle -= 1
            pan_pwm.ChangeDutyCycle(pan_angle)

        if tilt_dir == 'up' and tilt_angle < TILT_MAX:
            tilt_angle += 1
            tilt_pwm.ChangeDutyCycle(tilt_angle)

        elif tilt_dir == 'down' and tilt_angle > TILT_MIN:
            tilt_angle -= 1
            tilt_pwm.ChangeDutyCycle(tilt_angle)

        # print("pan anlge: ", pan_angle)
        # print("tilt angle: ", tilt_angle)
        time.sleep(servo_speed)




if __name__ == '__main__':
    try:
        threading.Thread(target=servo_loop, daemon='True').start()
        socketio.start_background_task(servo_loop)
        app.run(host='0.0.0.0', port=5000)
    finally:
        pan_pwm.stop()
        tilt_pwm.stop()
        GPIO.cleanup()


# Test Command: curl -X POST http://raspberrypi.local:5000/gpio/17/off




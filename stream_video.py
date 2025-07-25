from flask import Flask, request, jsonify, Response
import RPi.GPIO as GPIO
import cv2


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not start camera.")


def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            continue

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        jpg = buffer.tobytes()
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n'
        )

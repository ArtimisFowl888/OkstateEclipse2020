import RPi.GPIO as GPIO
import time

servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

b =3

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(2.5) # Initialization
try:
  while True:
    p.ChangeDutyCycle(5)
    p.ChangeDutyCycle(0)
    time.sleep(b)
    p.ChangeDutyCycle(7.5)
    p.ChangeDutyCycle(0)
    time.sleep(b)
    p.ChangeDutyCycle(10)
    p.ChangeDutyCycle(0)
    time.sleep(b)
    p.ChangeDutyCycle(12.5)
    p.ChangeDutyCycle(0)
    time.sleep(b)
    p.ChangeDutyCycle(10)
    p.ChangeDutyCycle(0)
    time.sleep(b)
    p.ChangeDutyCycle(7.5)
    p.ChangeDutyCycle(0)
    time.sleep(b)
    p.ChangeDutyCycle(5)
    p.ChangeDutyCycle(0)
    time.sleep(b)
    p.ChangeDutyCycle(2.5)
    p.ChangeDutyCycle(0)
    time.sleep(b)
except KeyboardInterrupt:
  p.stop()
  GPIO.cleanup()
import time
import board
import pulseio
import RPi.GPIO as GPIO
#from analogio import AnalogIn
 
# Pin setup
SERVO_PIN = 17
#FEEDBACK_PIN = board.A5
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
 
# Setup servo
servo = GPIO.PWM(SERVO_PIN, 50) # GPIO 17 for PWM with 50Hz
duty = 2
servo.start(0)
time.sleep(2)

while duty <= 10:
    servo.ChangeDutyCycle(duty)
    servo.ChangeDutyCycle(0)
    time.sleep(1)
    duty = duty + 1
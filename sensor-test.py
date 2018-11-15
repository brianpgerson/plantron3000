# External module imp
import RPi.GPIO as GPIO
import datetime
import time

init = False

GPIO.setmode(GPIO.BOARD) # Broadcom pin-numbering scheme
sensor_pin = 8
GPIO.setup(pin, GPIO.IN) 
count = 0
while count < 100: 
    print GPIO.input(pin)
    time.sleep(1)
    count += 1

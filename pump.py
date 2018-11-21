import RPi.GPIO as GPIO
import time

PUMP_INTERVAL = 5
PUMP_TIMES = 2
PUMP_SLEEP = 10

pump_power = 22

def execute_pump():
    GPIO.setmode(GPIO.BOARD) # Broadcom pin-numbering scheme
    GPIO.setup(pump_power, GPIO.OUT) 
    GPIO.output(pump_power, GPIO.HIGH)

    pumps = 0

    while (pumps < PUMP_TIMES):
        print('ENGAGING PUMP FOR ' + str(PUMP_INTERVAL) + ' seconds!')
        GPIO.output(pump_power, GPIO.LOW)
        time.sleep(PUMP_INTERVAL)
        GPIO.output(pump_power, GPIO.HIGH)
        print('PUMP COMPLETE')
        time.sleep(PUMP_SLEEP)
        pumps += 1
    
    print('ALL PUMPS COMPLETE')
    GPIO.cleanup()

execute_pump()

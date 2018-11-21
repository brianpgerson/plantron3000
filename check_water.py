import time
import RPi.GPIO as GPIO
import Adafruit_ADS1x15
import sys
import sqlite3
from datetime import datetime, timedelta

adc = Adafruit_ADS1x15.ADS1115()
THRESHOLD = 20000
GAIN = 1

PUMP_INTERVAL = 5
PUMP_TIMES = 2
PUMP_SLEEP = 10

SENSOR_READING_TIMES = 5
SENSOR_SLEEP = 1

sensor_power_pin = 29
read_pin = 0
pump_power = 22

DB = None

def execute_pump():
    pumps = 0
    time.sleep(PUMP_INTERVAL)
    while (pumps < PUMP_TIMES):
        print('ENGAGING PUMP FOR ' + str(PUMP_INTERVAL) + ' seconds!')
        GPIO.output(pump_power, GPIO.LOW)
        time.sleep(PUMP_INTERVAL)
        GPIO.output(pump_power, GPIO.HIGH)
        print('PUMP COMPLETE')
        time.sleep(PUMP_SLEEP)
        pumps += 1

    print('ALL PUMPS COMPLETE')

def check_for_auto_water(database):
    checks = 0
    readings = []
    did_pump = 0

    while (checks < SENSOR_READING_TIMES):
        print('reading pin value')
        GPIO.output(sensor_power_pin, GPIO.HIGH)
        value = adc.read_adc(read_pin, gain=GAIN)
        print('current moisture level is ' + str(value) + '. Threshold is ' + str(THRESHOLD))
        GPIO.output(sensor_power_pin, GPIO.LOW)
        readings.append(value)
        checks += 1
        time.sleep(SENSOR_SLEEP)

    average_value = sum(readings) / float(len(readings))

    print('last ten readings:')
    c = database.cursor()
    c.execute('SELECT * FROM moisture_readings ORDER BY id DESC LIMIT 10')
    rows = c.fetchall()
    for row in rows:
        print(row)

    if (average_value < THRESHOLD):
        print('checking DB for last watering!!!!')
        cursor = database.cursor();
        cursor.execute('SELECT * FROM moisture_readings WHERE did_pump=1 ORDER BY id DESC');
        last_reading = cursor.fetchone()

        if (last_reading == None or long_enough_ago(last_reading)):
	    print('last watering was more than 5 days ago. initiating pump sequence')
            execute_pump()
            did_pump = 1

    save_reading(database, did_pump, average_value)
    database.close()

def save_reading(database, did_pump, value):
    cursor = database.cursor()
    cursor.execute('''INSERT INTO moisture_readings (moisture_level, did_pump, date, time) VALUES  (?, ?, date('now'), time('now'))''', (value, did_pump))
    database.commit()
    print('saved reading to DB')

def long_enough_ago(reading):
    date_str = reading['date']
    time_str = reading['time']

    raw = ' '.join(date_str.split('-'))  + ' ' + ' '.join(time_str.split(':')[0:2])
    dt_obj = datetime.strptime(raw, '%Y %m %d %H %M')

    print('last reading that resulted in watering was: ')
    print(dt_obj)

    five_days_ago = datetime.now() - timedelta(days=5)
    return dt_obj < five_days_ago

def setup_pi(): 
    GPIO.setmode(GPIO.BOARD) # Broadcom pin-numbering scheme
    print('read_pin is ' + str(read_pin))
    print('sensor_power_pin is ' + str(sensor_power_pin))
    print('setting pin output levels')
    GPIO.setup(sensor_power_pin, GPIO.OUT) 
    GPIO.setup(pump_power, GPIO.OUT) 
    GPIO.output(sensor_power_pin, GPIO.LOW)
    GPIO.output(pump_power, GPIO.HIGH)
    print('....setup complete')

def setup_db():
    dbconnect = sqlite3.connect("sensordata.db")
    dbconnect.row_factory = sqlite3.Row
    return dbconnect

def main():
    try:
        setup_pi()
        DB = setup_db()
        check_for_auto_water(DB)

    except KeyboardInterrupt:
        print('quitting normally and resetting GPIO pins')
    except Exception as e: 
        print('unhandled error! exiting after resetting GPIO pins')
        print(e)
    finally:
        GPIO.cleanup() 

main()

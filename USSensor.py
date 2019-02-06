import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BOARD)

GPIO_TRIGGER = 16
GPIO_ECHO = 18

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    #Sets TRIGGER to High
    print('Trigger High')
    GPIO.output(GPIO_TRIGGER, True)
    
    #Sets TRIGGER to Low
    time.sleep(0.00001)
    print('Trigger low')
    GPIO.output(GPIO_TRIGGER, False)
    
    StartTime = time.time()
    StopTime = time.time()
    
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
        print('Echo low')
    
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
        print('Echo High')
    
    TimeElapsed = StopTime - StartTime
    
    distance = (TimeElapsed * 34300) / 2
    
    return distance


def testing():
    print(GPIO.input(GPIO_ECHO))

try:
    while True:
        testing()
##        dist = distance()
        dist = 'a'
        print('Dist = ' + dist)
        time.sleep(1)
    
except KeyboardInterrupt:
    print('\nStopped by user.')
    GPIO.cleanup()
    
except Exception as e:
    print(e)
    GPIO.cleanup()
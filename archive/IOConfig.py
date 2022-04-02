import RPi.GPIO as GPIO

DOOR_OPENED = 35
READY_LED = 33

DOOR_CLOSED = 37

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(DOOR_OPENED, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(DOOR_CLOSED, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(READY_LED, GPIO.OUT)
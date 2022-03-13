import RPi.GPIO as GPIO

DOOR_OPENED = 35
OPEN_LED = 33

DOOR_CLOSED = 37
CLOSE_LED = 31

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(DOOR_OPENED, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(DOOR_CLOSED, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(OPEN_LED, GPIO.OUT)
    GPIO.setup(CLOSE_LED, GPIO.OUT)
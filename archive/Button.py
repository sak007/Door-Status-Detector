import RPi.GPIO as GPIO

BTN_LOW = 0
BTN_HIGH = 1
BTN_RELEASE = 2
BTN_PRESS = 3

class Button:
    # debounceTime is the time to sleep after a button release is detected, this prevents
    # the debounce effect, where the reading switches between low and high before finally settling
    # at low, only occurs on for button release using Radek's buttons
    def __init__(self, pin, debounceTime=.2):
        self.pin = pin
        self.lastState = GPIO.input(pin) # Track the last state of the button
        self.debounceTime = .2
    
    # Checks the state of the button and compares it to the last checked state
    # If the state has not changed, then we are waiting for button release or press,
    # If the state goes from high to low, then the button was released, 
    # If the state goes from low to high, then the button was pressed
    # Return True if button was pressed, False if the state has not changed or reset back to low
    def checkState(self):
        curState = GPIO.input(self.pin) # No change since last check
        if curState == self.lastState: 
            return BTN_NO_CHANGE
        elif curState == GPIO.LOW: # Hi -> Low, button release
            self.lastState = curState
            time.sleep(self.debounceTime)
            return BTN_RELEASE
        else: # Low -> Hi, btn press
            self.lastState = curState
            return BTN_PRESS

    def isOn(self):
        return GPIO.input(self.pin) == GPIO.HIGH
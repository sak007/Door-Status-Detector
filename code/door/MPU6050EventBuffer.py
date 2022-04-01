from collections import deque
import time
import math
from threading import Thread
from MPU6050 import MPU6050

"""
Reads from the given MPU6050 sensor into a buffer, storing each tuple of 
6 values corresponding to accelxyz and gyroxyz. Testing indicates that 
the raspberry pi 4 can only handle sample rates somewhere between 250-360.
"""
class MPU6050EventBuffer(Thread):
    def __init__(self, ssCheckTimeSec, ssCheckGxThrsld, mGXThrshld, mOffToOnDbSec, mOnToOffDbSec, sensor):
        super().__init__()
        # Make these parameters
        self.steadyStateCheckTimeSec = ssCheckTimeSec
        self.steadyStateCheckThreshold = ssCheckGxThrsld
        self.motionGXThrsld = mGXThrshld
        self.motionGXOffToOnDbCount = sensor.getSampleRate() * mOffToOnDbSec
        self.motionGXOnToOffDbCount = sensor.getSampleRate() * mOnToOffDbSec
        self.motionGXDbCountRem = self.motionGXOffToOnDbCount
        self.sensor = sensor
        self.steadyStateCheckGxBuffer = deque()
        self.steadyStateCheckBuffer = deque()
        self.eventBuffer = deque()
        self.steadySteateCheckCount = sensor.getSampleRate() * self.steadyStateCheckTimeSec
        self.eventBeingTracked = False  # Event capture in progress
        self.eventCaptured = False      # Event has been captured
        self.eventStartPoint = -1       # Index into event buffer for start of motion
        self.eventEndPoint = -1         # Index into event buffer for end of motion
        self.eventEndOfCaptureCount = 0 # Used to capture a bit more data after the end fo an event
        self.thread = Thread()
        self.stopF = False
        self.bufferEn = True
        self.autoCalCount = sensor.getSampleRate() * 3 # Three seconds of auto calibration time
        self.autoCalCountRem = self.autoCalCount
        self.autoCalGXVal = 0
        self.autoCalGYVal = 0
        self.autoCalGZVal = 0
        self.autoCalAXVal = 0
        self.autoCalAYVal = 0
        self.autoCalAZVal = 0
        self.autoCalComplete = False


    # private, activate by calling start()
    # Begins reading from the sensor into the buffer
    def run(self):
        self.running = True
        self.bufferEn = True
        while not self.stopF: 
            if self.bufferEn:
                self.runBuffer()
            else:
                time.sleep(.01)
        self.running = False

    # Sets the flags neceesssary to stop the buffering thread
    def stop(self, block=False):
        self.stopBuffering()
        self.stopF = True
        while block and self.running:
            time.sleep(.001)

    # private, reads data from the sensor buffer, may throw an exception
    # if the sensor FIFO buffer overflows
    def runBuffer(self):
        self.resetBuffer()

        while self.bufferEn:
            time.sleep(.05)
            if self.sensor.isDataAvailable(): # Check if there is data to read and for overflow
                numChunks = int(self.sensor.readBufferLen() / 12) # number of 12 byte chunks
                for i in range(numChunks): # Read and store the data
                    data = self.sensor.readBuffer()
                    gXData = data[3]

                    self.updateSteadyStateBuffer(data)

                    # Wait for the steady state buffer to fill up
                    if self.isSteadyStateBufferReady() == True:
                        isSteadyFlag = self.isSteadyState()

                        if self.autoCalComplete == True and self.eventCaptured == False:
                            # No Event Captured, Keep Checking...
                            if ((gXData < self.motionGXThrsld) and (gXData > -1 * self.motionGXThrsld)):
                                # Inside motion deadband
                                if self.eventBeingTracked == False:
                                    # No Motion, and not yet tracking event, reset counters
                                    self.motionGXDbCountRem  = self.motionGXOffToOnDbCount
                                    self.eventStartPoint = -1
                                else:
                                    # No Motion, but currently tracking event, record point
                                    # and start debouncing
                                    self.eventBuffer.append(data)
                                    if self.motionGXDbCountRem > 0:
                                        if self.eventEndPoint == -1:
                                            self.eventEndPoint = len(self.eventBuffer)
                                        self.motionGXDbCountRem -= 1
                                    else:
                                        self.eventBeingTracked = False
                                        self.eventCaptured = True
                                        print("Event Detected - Stop Capture")
                            else:
                                # Outside motion deadband
                                if self.eventBeingTracked == True:
                                    # Motion and event being tracked, reset counters
                                    self.eventBuffer.append(data)
                                    self.motionGXDbCountRem  = self.motionGXOnToOffDbCount
                                    self.eventEndPoint = -1                                    
                                else:
                                    if self.motionGXDbCountRem > 0:
                                        # Motion seen, track record point and start debouncing
                                        if self.eventStartPoint == -1:
                                            self.eventBuffer = self.steadyStateCheckBuffer.copy()
                                            self.eventStartPoint = len(self.eventBuffer)
                                        else:
                                            self.eventBuffer.append(data)                                            
                                        self.motionGXDbCountRem -= 1
                                    else:
                                        # Debounced motion, this is a real event
                                        self.eventBuffer.append(data)
                                        self.eventBeingTracked = True
                                        print("Event Detected - Start Capture")

                        elif self.autoCalComplete == False:
                            # Perform IMU Auto Calibration
                            if isSteadyFlag == False:
                                self.autoCalCountRem = self.autoCalCount
                                self.autoCalAXVal = 0
                                self.autoCalAYVal = 0
                                self.autoCalAZVal = 0
                                self.autoCalGXVal = 0
                                self.autoCalGYVal = 0
                                self.autoCalGZVal = 0
                            else:
                                self.autoCalCountRem -= 1
                                if self.autoCalCountRem > 0:
                                    self.autoCalAXVal += data[0]
                                    self.autoCalAYVal += data[1]
                                    self.autoCalAZVal += data[2]
                                    self.autoCalGXVal += data[3]
                                    self.autoCalGYVal += data[4]
                                    self.autoCalGZVal += data[5]
                                else:
                                    self.autoCalAXVal = self.autoCalAXVal / self.autoCalCount
                                    self.autoCalAYVal = self.autoCalAYVal / self.autoCalCount
                                    self.autoCalAZVal = self.autoCalAZVal / self.autoCalCount
                                    self.autoCalGXVal = self.autoCalGXVal / self.autoCalCount
                                    self.autoCalGYVal = self.autoCalGYVal / self.autoCalCount
                                    self.autoCalGZVal = self.autoCalGZVal / self.autoCalCount
                                    self.autoCalComplete = True
                                    print("Auto Cal Complete - AXOffset: " + str(self.autoCalAXVal) + ", AYOffset: " + str(self.autoCalAYVal) + ", AZOffset: " + str(self.autoCalAZVal) + ", GXOffset: " + str(self.autoCalGXVal) + ", GYOffset: " + str(self.autoCalGYVal) + ", GZOffset: " + str(self.autoCalGZVal))                        
                                    self.sensor.setSensorOffsets(
                                        self.autoCalAXVal, 
                                        self.autoCalAYVal,
                                        self.autoCalAZVal,
                                        self.autoCalGXVal,
                                        self.autoCalGYVal,
                                        self.autoCalGZVal)
                                    self.resetBuffer()
                                    break

        self.runningB = False

    def isCalibratedFlag(self):
        return self.autoCalComplete

    def updateSteadyStateBuffer(self,data):
        self.steadyStateCheckGxBuffer.append(data[3])
        self.steadyStateCheckBuffer.append(data)
        if len(self.steadyStateCheckGxBuffer) > self.steadySteateCheckCount:
            # Keep the steady state buffer at the correct size
            self.steadyStateCheckGxBuffer.popleft()
            self.steadyStateCheckBuffer.popleft()

    def isSteadyStateBufferReady(self):
        buffReadyFlag = False
        if len(self.steadyStateCheckGxBuffer) >= self.steadySteateCheckCount:       
            buffReadyFlag = True
        return buffReadyFlag

    # Helper function to tell if the sensor is in a steady state
    def isSteadyState(self):
        isSteadyFlag = False
        if self.isSteadyStateBufferReady() == True:
            if (max(self.steadyStateCheckGxBuffer) - min(self.steadyStateCheckGxBuffer) <= self.steadyStateCheckThreshold):
                isSteadyFlag = True
        return isSteadyFlag

    def checkForEvent(self):
        return self.eventCaptured

    def getEventStartPoint(self):
        if self.checkForEvent():
            return self.eventStartPoint
        return -1

    def getEventEndPoint(self):
        if self.checkForEvent():
            return self.eventEndPoint
        return -1

    def bufferLen(self):
        return len(self.eventBuffer)

    def resetBuffer(self):
        self.sensor.clearBuffer()
        self.steadyStateCheckGxBuffer.clear()
        self.steadyStateCheckBuffer.clear()
        self.eventBuffer.clear()
        self.runningB = True
        self.eventBeingTracked = False
        self.eventCaptured = False
        self.eventStartPoint = -1
        self.eventEndPoint = -1        
        self.eventEndOfCaptureCount = 0

    def clearEvent(self):
        self.eventCaptured = False
        self.eventBuffer.clear()
        self.eventStartPoint = -1
        self.eventEndPoint = -1

    # Reads a 6 tuple of sensor data from the buffer
    def read(self):
        if self.bufferLen() != 0:
            return self.eventBuffer.popleft()

    def startBuffering(self):
        self.bufferEn = True

    def stopBuffering(self, block=False):
        self.bufferEn = False
        while block:
            time.sleep(.001)

    # Reads a 6 tuple of sensor data from the buffer w/o removing it
    def peek(self, i):
        if i < self.bufferLen():
            return self.buffer[i]
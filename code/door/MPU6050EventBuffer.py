from collections import deque
import time
import math
import statistics
from threading import Thread
from MPU6050 import MPU6050

"""
Reads from the given MPU6050 sensor into a buffer, storing each tuple of 
6 values corresponding to accelxyz and gyroxyz. Testing indicates that 
the raspberry pi 4 can only handle sample rates somewhere between 250-360.
"""
class MPU6050EventBuffer(Thread):
    def __init__(self, ssCheckTimeSec, ssCheckGxThrshld, mGXSigmaThrshld, mOffToOnDbSec, mOnToOffDbSec, sensor):
        super().__init__()
        # Make these parameters
        self.steadyStateCheckTimeSec = ssCheckTimeSec
        self.steadyStateCheckThreshold = ssCheckGxThrshld
        self.motionGXSigmaThrsld = mGXSigmaThrshld
        self.motionGXThrsld = 0         # Determined during autocalibration
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
        self.autoCalData = {"ax":[],"ay":[],"az":[],"gx":[],"gy":[],"gz":[]}
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
                                self.autoCalData["ax"].clear()
                                self.autoCalData["ay"].clear()
                                self.autoCalData["az"].clear()
                                self.autoCalData["gx"].clear()
                                self.autoCalData["gy"].clear()
                                self.autoCalData["gz"].clear()
                                self.autoCalAXVal = 0
                                self.autoCalAYVal = 0
                                self.autoCalAZVal = 0
                                self.autoCalGXVal = 0
                                self.autoCalGYVal = 0
                                self.autoCalGZVal = 0
                            else:
                                self.autoCalCountRem -= 1
                                if self.autoCalCountRem > 0:
                                    self.autoCalData["ax"].append(data[0])
                                    self.autoCalData["ay"].append(data[1])
                                    self.autoCalData["az"].append(data[2])
                                    self.autoCalData["gx"].append(data[3])
                                    self.autoCalData["gy"].append(data[4])
                                    self.autoCalData["gz"].append(data[5])
                                else:
                                    self.autoCalAXVal = sum(self.autoCalData["ax"])/len(self.autoCalData["ax"])
                                    self.autoCalAYVal = sum(self.autoCalData["ay"])/len(self.autoCalData["ay"])
                                    self.autoCalAZVal = sum(self.autoCalData["az"])/len(self.autoCalData["az"])
                                    self.autoCalGXVal = sum(self.autoCalData["gx"])/len(self.autoCalData["gx"])
                                    self.autoCalGYVal = sum(self.autoCalData["gy"])/len(self.autoCalData["gy"])
                                    self.autoCalGZVal = sum(self.autoCalData["gz"])/len(self.autoCalData["gz"])
                                    self.motionGXThrsld = statistics.stdev(self.autoCalData["gx"]) * self.motionGXSigmaThrsld
                                    self.autoCalData["ax"].clear()
                                    self.autoCalData["ay"].clear()
                                    self.autoCalData["az"].clear()
                                    self.autoCalData["gx"].clear()
                                    self.autoCalData["gy"].clear()
                                    self.autoCalData["gz"].clear()
                                    self.sensor.setSensorOffsets(
                                        self.autoCalAXVal, 
                                        self.autoCalAYVal,
                                        self.autoCalAZVal,
                                        self.autoCalGXVal,
                                        self.autoCalGYVal,
                                        self.autoCalGZVal)
                                    self.resetBuffer()
                                    print("Auto Cal Complete - Motion Threshold: " + str(self.motionGXThrsld) + ", AXOffset: " + str(self.autoCalAXVal) + ", AYOffset: " + str(self.autoCalAYVal) + ", AZOffset: " + str(self.autoCalAZVal) + ", GXOffset: " + str(self.autoCalGXVal) + ", GYOffset: " + str(self.autoCalGYVal) + ", GZOffset: " + str(self.autoCalGZVal))                        
                                    self.autoCalComplete = True
                                    break

        self.runningB = False

    # Helper function stating if the auto calibration is complete
    def isCalibratedFlag(self):
        return self.autoCalComplete

    # Adds latest IMU data to the steady state buffer and removes the oldest data when necessary
    def updateSteadyStateBuffer(self,data):
        self.steadyStateCheckGxBuffer.append(data[3])
        self.steadyStateCheckBuffer.append(data)
        if len(self.steadyStateCheckGxBuffer) > self.steadySteateCheckCount:
            # Keep the steady state buffer at the correct size
            self.steadyStateCheckGxBuffer.popleft()
            self.steadyStateCheckBuffer.popleft()

    # Helper function stating if the steady state buffer has enough data to make a decision
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

    # Helper function stating if a motion event has been captured
    def checkForEvent(self):
        return self.eventCaptured

    # Returns the index to the start of motion event in the event buffer
    def getEventStartPoint(self):
        if self.checkForEvent():
            return self.eventStartPoint
        return -1

    # Returns the index to the end of motion event in the event buffer
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

    # Clears the captured events and allows capturing of another event
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

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
    def __init__(self, ssCheckTimeSec, ssCheckOnGxThrsld, ssCheckOffGxThrsld, sensor):
        super().__init__()
        # Make these parameters
        self.steadyStateCheckTimeSec = ssCheckTimeSec
        self.steadyStateCheckOnThreshold = ssCheckOnGxThrsld
        self.steadyStateCheckOffThreshold = ssCheckOffGxThrsld

        self.sensor = sensor
        self.steadyStateCheckGxBuffer = deque()
        self.steadyStateCheckBuffer = deque()
        self.eventBuffer = deque()
        self.steadySteateCheckCount = sensor.getSampleRate() * self.steadyStateCheckTimeSec
        self.eventBeingTracked = False
        self.eventCaptured = False
        self.eventJustCleared = False
        self.eventStartPoint = -1
        self.eventEndPoint = -1
        self.eventEndOfCaptureCount = 0
        self.gXOffset = 0
        self.thread = Thread()
        self.stopF = False
        self.bufferEn = True


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
        self.sensor.clearBuffer()
        self.steadyStateCheckGxBuffer.clear()
        self.steadyStateCheckBuffer.clear()
        self.eventBuffer.clear()
        self.runningB = True
        self.eventBeingTracked = False
        self.eventCaptured = False
        self.eventJustCleared = False
        self.eventStartPoint = -1
        self.eventEndPoint = -1        
        self.eventEndOfCaptureCount = 0

        while self.bufferEn:
            time.sleep(.05)
            if self.sensor.isDataAvailable(): # Check if there is data to read and for overflow
                numChunks = int(self.sensor.readBufferLen() / 12) # number of 12 byte chunks
                for i in range(numChunks): # Read and store the data
                    data = self.sensor.readBuffer()

                    self.steadyStateCheckGxBuffer.append(data[3])
                    self.steadyStateCheckBuffer.append(data)

                    if self.eventCaptured != True and self.eventJustCleared != True:
                        self.eventBuffer.append(data)
                    elif self.eventCaptured != True and self.eventJustCleared == True:
                        self.eventBuffer = self.steadyStateCheckBuffer.copy()
                        self.eventJustCleared = False

                    # Wait for the steady state buffer to fill up
                    if len(self.steadyStateCheckGxBuffer) > self.steadySteateCheckCount:
                        # Keep the steady state buffer at the correct size
                        self.steadyStateCheckGxBuffer.popleft()
                        self.steadyStateCheckBuffer.popleft()
                        
                        if self.eventBeingTracked != True and self.eventCaptured != True: 
                            self.eventBuffer.popleft()

                        # If the delta values in the buffer show movement, start the capture
                        if ((max(self.steadyStateCheckGxBuffer) - min(self.steadyStateCheckGxBuffer) > self.steadyStateCheckOnThreshold) and
                            (self.eventCaptured == False)):
                            self.eventBeingTracked = True
                            self.eventEndPoint = -1

                            if self.eventStartPoint == -1:
                                self.eventStartPoint = len(self.eventBuffer)

                            self.eventEndOfCaptureCount = math.floor(self.steadySteateCheckCount / 2)

                        # If the delta values in the buffer show steady state, stop the capture
                        elif ((max(self.steadyStateCheckGxBuffer) - min(self.steadyStateCheckGxBuffer) < self.steadyStateCheckOffThreshold) and
                            (self.eventBeingTracked == True)):
                            if self.eventEndPoint == -1:
                                self.eventEndPoint = len(self.eventBuffer) - self.steadySteateCheckCount

                            if self.eventEndOfCaptureCount > 0:
                                self.eventEndOfCaptureCount -= 1
                            else:
                                self.eventBeingTracked = False
                                self.eventCaptured = True                        
        self.runningB = False

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

    def clear(self):
        self.eventCaptured = False
        self.eventBuffer.clear()
        self.eventJustCleared = True
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

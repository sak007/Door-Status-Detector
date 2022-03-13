from collections import deque
import time
from threading import Thread
from MPU6050 import MPU6050

"""
Reads from the given MPU6050 sensor into a buffer, storing each tuple of 
6 values corresponding to accelxyz and gyroxyz. Testing indicates that 
the raspberry pi 4 can only handle sample rates somewhere between 250-360.
"""
class MPU6050Buffer(Thread):
    def __init__(self, sensor):
        super().__init__()
        self.sensor = sensor
        self.buffer = deque()
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
        self.buffer.clear()
        while self.bufferEn:
            time.sleep(.05)
            if self.sensor.isDataAvailable(): # Check if there is data to read and for overflow
                numChunks = int(self.sensor.readBufferLen() / 12) # number of 12 byte chunks
                for i in range(numChunks): # Read and store the data
                    data = self.sensor.readBuffer()
                    self.buffer.append(data)
                    # print("data", data)
            # else:
            #     time.sleep(.005)

    def startBuffering(self):
        self.bufferEn = True

    def stopBuffering(self):
        self.bufferEn = False

    def bufferLen(self):
        return len(self.buffer)

    # Reads a 6 tuple of sensor data from the buffer
    def read(self):
        if self.bufferLen() != 0:
            return self.buffer.popleft()

    # Reads a 6 tuple of sensor data from the buffer w/o removing it
    def peek(self, i):
        if i < self.bufferLen():
            return self.buffer[i]

# Tests the buffer
def main():
    sensor = MPU6050(sampleRate=200)
    buf = MPU6050Buffer(sensor)
    time.sleep(.05)
    assert buf.bufferLen() == 0 # Check to make sure buffering hasnt started
    assert buf.read() == None
    buf.start()
    time.sleep(.05)
    assert buf.bufferLen() != 0 # Buffering started, should have some values
    # Let sample for 10 seconds and check the number of values recorded
    mytime = .05
    while True:
        a = time.time()
        buflen = buf.bufferLen()
        for i in range(buflen):
            b = buf.read()
            
        print(time.time() - a, " to read ", buflen, " chunks")
    for i in range(3):
        time.sleep(10)
        mytime += 10
        print(buf.bufferLen() / mytime, " Hz")
    # Check that peek doesn't remove anything from the buffer
    assert buf.peek(0) == buf.read()
    print(buf.read())
    buf.stop()


if __name__ == "__main__":
    main()

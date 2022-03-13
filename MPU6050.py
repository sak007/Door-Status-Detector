import time
import smbus

from MPU6050Constants import *

""" Class to interact with MPU6050 sensor
-Sensor values are 16 bits and represent a % value based on the given full range
 at initialization. The output from a register is then -32768 <-> 32767 corresponding
 to -100% to 100%
-Generally want to avoid reading live and read from the buffer instead to avoid
 syncrhonization issues between the live user registers where sensor values are stored
-Reading from the buffer guarentees that the sensor values were all sampled at the same
 time
"""
class MPU6050:
    """Initializes the MPU6050 sensor using I2C
        -sampleRate (Hz), Frequency sensors will be sampled at, can't get exact rate,
         due to the way the divider is calculated
        -gRange (degrees/s) desired output range for gyro scope signals
        -aRange (g (9.81 m/s^2)) desired output range for accel signals"""   
    def __init__(self, sampleRate=25, gRange=250, aRange=2):
        self.bus = smbus.SMBus(1) # start comm with i2c bus
        # Sample Rate Divider Register - divides the base sample rate 8000Hz so that the given
        # sampleRate is achieved, 
        assert sampleRate <= 1000
        sampleRateDivier = (8000 / sampleRate) - 1
        print("divider:", sampleRateDivier)
        self.bus.write_byte_data(MPU6050_ADDR, SMPLRT_DIV, int(sampleRateDivier))
        time.sleep(0.1)
        # Power Management/Crystal Register
        time.sleep(0.1)
        self.bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0x00)
        time.sleep(0.1)
        self.bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0x01)
        time.sleep(0.1)
        # Config register - FSYNC/Low Pass Filter - Disable w/ 0
        self.bus.write_byte_data(MPU6050_ADDR, CONFIG, 0)
        time.sleep(0.1)
        # Gyro Full Range Config Register
        assert gRange in GConfigVal
        self.gRange = gRange
        gSel = GConfigSel[GConfigVal.index(gRange)]
        self.bus.write_byte_data(MPU6050_ADDR, GYRO_CONFIG, gSel)
        time.sleep(.1)
        # Accelerometer Full Range Config Register
        assert aRange in AConfigVal
        self.aRange = aRange
        aSel = int(AConfigSel[AConfigVal.index(aRange)])
        self.bus.write_byte_data(MPU6050_ADDR, ACCEL_CONFIG, aSel)
        time.sleep(.1)
        # Enable FIFO Buffer Signal Saving, bits correspond to signals
        # Bit Order: temp, xg, yg, zg, accel, slv2, slv1, slv0 
        # 0x78 means record accelerometer and gyro signals
        # Changing this means you will need to change the readBuffer() func
        self.bus.write_byte_data(MPU6050_ADDR, FIFO_EN, 0x78)
        time.sleep(0.1)
        # Reset the FIFO buffer
        self.clearBuffer()

    # Reads from 2 8 byte registers in high, low order and 
    # returns the int form of the reading
    def readRegister16(self, reg):
        # read accel and gyro values
        high = self.bus.read_byte_data(MPU6050_ADDR, reg)
        low = self.bus.read_byte_data(MPU6050_ADDR, reg+1)
        return twosComplement2Int(combineBytes(high, low))

    # Scales the 16 bit accel value based on the full range
    def scaleAccel(self, val):
        return (val / 2**15) * self.aRange

    # Scales the 16 bit gyro value based on the full range
    def scaleGyro(self, val):
        return (val / 2**15) * self.gRange

    # Reads accel and gyro sensor values from the user registers
    # and scales them based on the range chosen at initialization
    # Note, not guarenteed to be synchronously sampled, use for 
    # debug only
    def readLive(self):
        accX = self.scaleAccel(self.readRegister16(ACCEL_XOUT_H))
        accY = self.scaleAccel(self.readRegister16(ACCEL_YOUT_H))
        accZ = self.scaleAccel(self.readRegister16(ACCEL_ZOUT_H))
        
        gyroX = self.scaleGyro(self.readRegister16(GYRO_XOUT_H))
        gyroY = self.scaleGyro(self.readRegister16(GYRO_YOUT_H))
        gyroZ = self.scaleGyro(self.readRegister16(GYRO_ZOUT_H))
        return accX, accY, accZ, gyroX, gyroY, gyroZ

    # Returns the # of bytes in the FIFO buffer
    # 2 bytes per sensor measurement, 1024 is the size limit
    def readBufferLen(self):
        return self.readRegister16(FIFO_COUNT_H)

    # Resets the FIFO buffer count to 0
    def clearBuffer(self):
        self.bus.write_byte_data(MPU6050_ADDR, USER_CTRL, 0x44)

    # Reads 2 bytes from the FIFO buffer, merges them and converts from
    # 2s complement
    def readBuffer16(self):
        # read accel and gyro values
        high = self.bus.read_byte_data(MPU6050_ADDR, FIFO_R_W)
        low = self.bus.read_byte_data(MPU6050_ADDR, FIFO_R_W)
        return twosComplement2Int(combineBytes(high, low))

    # Reads accel and gyro burst from the FIFO buffer
    def readBuffer(self):
        accX = self.scaleAccel(self.readBuffer16())
        accY = self.scaleAccel(self.readBuffer16())
        accZ = self.scaleAccel(self.readBuffer16())
        
        gyroX = self.scaleGyro(self.readBuffer16())
        gyroY = self.scaleGyro(self.readBuffer16())
        gyroZ = self.scaleGyro(self.readBuffer16())
        return accX, accY, accZ, gyroX, gyroY, gyroZ

    def readBufferRaw(self):
        accX = self.readBuffer16()
        accY = self.readBuffer16()
        accZ = self.readBuffer16()
        
        gyroX = self.readBuffer16()
        gyroY = self.readBuffer16()
        gyroZ = self.readBuffer16()
        return accX, accY, accZ, gyroX, gyroY, gyroZ

    # Checks to see if data is avaialbe in the buffer
    # Since we read from 6 channels, we need 12 bytes
    # If len is 1024, that means we lost the oldest data
    def isDataAvailable(self):
        bufferlen = self.readBufferLen()
        if bufferlen == 1024:
            raise Exception("MPU06050 FIFO Buffer overflow")
        elif bufferlen < 12: # Not ready
            return False
        else: # Ready
            return True

    # Clears the buffer and waits until the accel and
    # gyro signals have been synchronously sampled, then reads
    # and returns them
    # Use if you want a single synchrnously sampled reading of all channels 
    def singleSyncRead(self, sleepTime=.001):
        self.clearBuffer()
        while not self.isDataAvailable():
            time.sleep(sleepTime)
        return self.readBuffer()

# Combines a high and low byte
def combineBytes(high, low):
    return ((high << 8) | low)

# Converts a 16 bit value from 2s complement to int
def twosComplement2Int(val):
    if(val > 32768): # Negative Value
        val -= 65536
    return val

def stringifyVals(vals):
    mystr = "{:4.2f}".format(vals[0])
    for val in vals[1:]:
        mystr += ", " + "{:4.2f}".format(val)
    print(mystr)
    
# Tests the MPU6050 by reading from the buffer and then the raw registers
# Values shoyld be the same or close, unles the decice is moving and the sample
# rate is high
# Looking at the bufferLen gives an idea of how fast the buffer fills up
# For a sample rate of 32HZ, we get 2 bytes per signal and have 6 channels, so
# we expect that the buffer gets 384 values per second
def main():
    sensor = MPU6050()
    while True:
        buff = sensor.singleSyncRead()
        live = sensor.readLive()
        print("Live, Buffer")
        stringifyVals(live)
        stringifyVals(buff)
        time.sleep(.5)
        print("Buffer len:", sensor.readBufferLen())

if __name__ == "__main__":
    main()


    
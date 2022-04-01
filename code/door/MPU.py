import smbus
from time import sleep

class MPU:
    def __init__(self):
        self.ACC = 0
        self.GYRO = 1

        self.PWR_MGMT_1   = 0x6B
        self.SMPLRT_DIV   = 0x19
        self.CONFIG       = 0x1A
        self.GYRO_CONFIG  = 0x1B
        self.INT_ENABLE   = 0x38
        self.ACCEL_XOUT_H = 0x3B
        self.ACCEL_YOUT_H = 0x3D
        self.ACCEL_ZOUT_H = 0x3F
        self.GYRO_XOUT_H  = 0x43
        self.GYRO_YOUT_H  = 0x45
        self.GYRO_ZOUT_H  = 0x47
        self.DEVICE_ADDR  = 0x68
        self.bus = smbus.SMBus(1)

        # add info to register
        self.bus.write_byte_data(self.DEVICE_ADDR, self.SMPLRT_DIV, 7)
        self.bus.write_byte_data(self.DEVICE_ADDR, self.PWR_MGMT_1, 1)
        self.bus.write_byte_data(self.DEVICE_ADDR, self.CONFIG, 0)
        self.bus.write_byte_data(self.DEVICE_ADDR, self.GYRO_CONFIG, 24)
        self.bus.write_byte_data(self.DEVICE_ADDR, self.INT_ENABLE, 1)

    def read_raw_data(self, addr):
        #Accelero and Gyro value are 16-bit
        high = self.bus.read_byte_data(self.DEVICE_ADDR, addr)
        low = self.bus.read_byte_data(self.DEVICE_ADDR, addr+1)

        #concatenate higher and lower value
        value = ((high << 8) | low)

        # to get signed value from mpu6050
        if value > 32768:
            value = value - 65536
        return value

    def get_data_by_addr(self, addr):
        raw_data = self.read_raw_data(addr)
        data = raw_data
        if addr in [self.ACCEL_XOUT_H, self.ACCEL_YOUT_H, self.ACCEL_ZOUT_H]:
            return data / 16384.0
        elif addr in [self.GYRO_XOUT_H, self.GYRO_YOUT_H, self.GYRO_ZOUT_H]:
            return data / 131.0
        else:
            print('Invalid address')

    def get_data(self, event):
        x = y = z = None
        if event == self.ACC:
            x = self.get_data_by_addr(self.ACCEL_XOUT_H)
            y = self.get_data_by_addr(self.ACCEL_YOUT_H)
            z = self.get_data_by_addr(self.ACCEL_ZOUT_H)
        elif event == self.GYRO:
            x = self.get_data_by_addr(self.GYRO_XOUT_H)
            y = self.get_data_by_addr(self.GYRO_YOUT_H)
            z = self.get_data_by_addr(self.GYRO_ZOUT_H)
        return { 'x': x, 'y': y, 'z': z }

if __name__ == "__main__":
    MPU = MPU()
    while True:
        print ('Acc: ', MPU.get_data(MPU.ACC))
        print ('Gyro: ', MPU.get_data(MPU.GYRO))
        sleep(0.1)

#https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf
#https://cdn.sparkfun.com/datasheets/Sensors/Accelerometers/RM-MPU-6000A.pdf

# MPU6050 Registers
MPU6050_ADDR = 0x68 # I2C address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
ACCEL_CONFIG = 0x1C
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
TEMP_OUT_H   = 0x41
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47
FIFO_EN  = 0x23
USER_CTRL = 0x6A
FIFO_R_W = 0x74
FIFO_COUNT_H = 0x72

# Gyro full range output options, maps to the byte values in GyroConfigSel
GConfigVal = [250,500,1000,2000] # degrees/sec
# Byte values for the GYRO_CONFIG sensor to set the full range of gyro output
GConfigSel = [0b00000,0b010000,0b10000,0b11000]
# Ex if you wanted your gyro output to be +- 250 degrees/second, you would send
# 0b0000 to the GYRO_CONFIG register

# Accelerometer full range output options, maps to the byte values in AConfigSel
AConfigVal = [2,4,8,16] # g (g = 9.81 m/s^2)
# Byte values for the ACCEL_CONFIG sensor to set the full range of accelerometer output
AConfigSel = [0b00000,0b01000,0b10000,0b11000]
# Ex if you wanted your accelerometer output to be +- 2 g, you would send
# 0b0000 to the ACCEL_CONFIG register


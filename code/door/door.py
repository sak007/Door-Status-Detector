
from MPU import MPU
from wiotpClient import DeviceClient
from time import sleep
import traceback

try:
    MPU = MPU()
    client = DeviceClient()
    while True:
        acc = MPU.get_data(MPU.ACC)
        gyro = MPU.get_data(MPU.GYRO)
        print ('Acc: ', acc)
        print ('Gyro: ', gyro)
        client.publish('ACC', acc)
        client.publish('GYRO', gyro)

        sleep(0.1)
except Exception as e:
    print("Exception: ", e)
    traceback.print_exc()

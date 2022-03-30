from wiotpClient import DeviceClient
import time
import os, json
import uuid

try:
    client = DeviceClient()
    while True:
        eventData = {'Test' : True}
        client.publish('door', eventData)
        time.sleep(5)

except Exception as e:
    print("Exception: ", e)

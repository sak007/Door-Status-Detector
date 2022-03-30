from wiotpClient import Client
import time
import os, json
import wiotp.sdk.application
import uuid

try:
    while True:
        client = Client()
        eventData = {'Test' : True}
        client.publish('door', eventData)
        time.sleep(5)
except Exception as e:
    print("Exception: ", e)

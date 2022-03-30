import wiotp.sdk.device
import json
import uuid

class Client:

    def __init__(self):
        f = open('../properties.json')
        properties = json.load(f)
        self.typeId = properties['DEVICE_TYPE']
        self.deviceId = properties['DEVICE_ID']
        options = wiotp.sdk.device.parseConfigFile("device.yaml")
        self.client = wiotp.sdk.device.DeviceClient(config=options)
        self.client.connect()

    def publish(self, eventId, eventData):
        self.client.publishEvent(eventId=eventId, msgFormat="json", data=eventData, qos=2, onPublish=self.publishEventCallback)

    def publishEventCallback(self):
        print ("Event data published!")

import wiotp.sdk.application
import json

class Client:

    def __init__(self):
        f = open('../properties.json')
        properties = json.load(f)
        self.typeId = properties['DEVICE_TYPE']
        self.deviceId = properties['DEVICE_ID']
        options = wiotp.sdk.application.parseConfigFile("../application.yaml")
        self.client = wiotp.sdk.application.ApplicationClient(config=options)

    def connect(self):
        self.client.connect()

    def subscribe(self, eventId):
        self.client.subscribeToDeviceEvents(eventId=eventId)

    def publish(self, eventId, eventData):
        self.client.publishEvent(typeId=self.typeId, deviceId=self.deviceId, eventId=eventId, msgFormat="json", data=eventData, onPublish=self.publishEventCallback)

    def publishEventCallback(self):
        print ("Event data published!")

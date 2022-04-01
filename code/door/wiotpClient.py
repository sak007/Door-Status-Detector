import wiotp.sdk.device
import json
import uuid

class DeviceClient:

    def __init__(self):
        f = open('../../properties.json')
        properties = json.load(f)
        self.typeId = properties['DEVICE_TYPE']
        self.deviceId = properties['DEVICE_ID']
        options = wiotp.sdk.device.parseConfigFile("../device.yaml")
        self.client = wiotp.sdk.device.DeviceClient(config=options)
        self.client.connect()

    def publish(self, eventId, eventData):
        self.client.publishEvent(eventId=eventId, msgFormat="json", data=eventData, qos=2, onPublish=self.publishEventCallback)

    def publishEventCallback(self):
        print ("Event data published!")

if __name__ == "__main__":
    try:
        client = DeviceClient()
        while True:
            eventData = {'Test' : True}
            client.publish('door', eventData)
            sleep(5)

    except Exception as e:
        print("Exception: ", e)

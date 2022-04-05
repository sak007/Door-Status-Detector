import wiotp.sdk.application
import json
import uuid

class ApplicationClient:

    def __init__(self):
        f = open('../../properties.json')
        properties = json.load(f)
        self.typeId = properties['MONITOR']['DEVICE_TYPE']
        self.deviceId = properties['MONITOR']['DEVICE_ID']
        options = wiotp.sdk.application.parseConfigFile("application.yaml")
        self.client = wiotp.sdk.application.ApplicationClient(config=options)
        self.client.connect()
        self.client.deviceEventCallback = self.onMessage

    def sendCommand(self, commandId, data):
        self.client.publishCommand(self.typeId, self.deviceId, commandId, "json", data)
        print('Published data')

    def onMessage(self, event):
        print(event.eventId, event.data)


if __name__ == "__main__":
    try:
        client = DeviceClient()
        while True:
            eventData = {'Test' : True}
            client.publish('door', eventData)
            sleep(5)

    except Exception as e:
        print("Exception: ", e)

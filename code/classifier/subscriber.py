from wiotpApplicationClient import ApplicationClient

class ClassifierAppClient(ApplicationClient):
    def onMessage(self, event):
        if event.eventId == 'imu':
            # TODO: Call respective classifier
            print(event.eventId, event.data)

            # Process data and send decision
            status = 'open'
            data = {"status": status}
            self.sendCommand('doorCommand', data)

if __name__ == '__main__':
    try:
        client = ClassifierAppClient()
        client.client.subscribeToDeviceEvents(eventId="imu")
        while True:
            pass
    except Exception as e:
        print("Exception: ", e)

from wiotpApplicationClient import ApplicationClient
import numpy as np
import tensorflow as tf
import copy

MaxSamples = 600 # Num Gx Samples for Model
MODEL_PATH = "myModel"

def normalize(data):
    mean = np.mean(data)
    sd = np.std(data)
    data2 = (data - mean) / sd
    return list(data2)

# Fills data list up until the length matches n
def fill(data, n, val=0):
    data2 = copy.deepcopy(data)
    diff = n - len(data2)
    for i in range(diff):
        data2.append(0)
    return data2

# Normalizes data and puts it into the correct shape for the model
def preprocessData(data):
    data = normalize(data)
    data = fill(data, MaxSamples)
    return np.dstack([data])

# Given the prepreocessed gx
def predict(model, data):
    result = np.argmax(model.predict(preprocessData(data)))
    if result == 0:
        return "close"
    else:
        return "open"

# Load the nn model
def initModel(path):
    return tf.keras.models.load_model(path)

class ClassifierAppClient(ApplicationClient):
    def __init__(self):
        super(ClassifierAppClient, self).__init__()
        self.model = initModel(MODEL_PATH)
    def onMessage(self, event):
        if event.eventId == 'imu':
            print(event.eventId, event.data)
            status = predict(self.model, event.data["gx"])
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

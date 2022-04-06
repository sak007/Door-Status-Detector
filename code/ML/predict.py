import tensorflow as tf
import numpy as np
import os
import copy

MODEL_PATH = "code/ML/myModel"

TestFolder = "data/jppahl/"

MaxSamples = 600 # Num Gx Samples for Model


def getClass(file):
    c = (file[:-4].split("_")[1])
    if c == "c":
        return 0
    elif c =="o":
        return 1
    else:
        raise Exception("Unknown class")

# Read the gx data from start:stop
def readData(file):
    data = []
    with open(file, "r") as f:
        lines = f.readlines()
        start = int(lines[4].split(",")[1])
        stop = int(lines[5].split(",")[1])
        myclass = getClass(file)
        gx = lines[9].split(",")
        assert gx[0] == "gx"
        for val in gx[start:stop]:
            data.append(float(val))
    return data, myclass

# Create a list of n lists
def nList(n):
    myList = []
    for i in range(n):
        myList.append([])
    return myList

# Down sample a list of data into factor lists
def downsample(data, factor):
    downData = nList(factor)
    nValsPerSplit = int(len(data) / factor)
    for i in range(nValsPerSplit):
        for j in range(factor):
            index = i * factor + j
            downData[j].append(data[index])
    return downData

def downsampleToNPoints(data, n):
    if len(data) > n:     
        factor = 2
        while True:
            dVals = downsample(data,factor)[0]
            if len(dVals) < MaxSamples:
                break
            else:
                factor += 1
        return dVals, factor
    return data, 1

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
    data, _ = downsampleToNPoints(data, MaxSamples)
    data = normalize(data)
    data = fill(data, MaxSamples)
    return np.dstack([data])

def predict(model, data):
    predictRaw = model.predict(data)
    return np.argmax(predictRaw)

# This is to test out loading a saved model and having it predict against data
# defined in the files in MyFolder. 
def main():
    myModel = tf.keras.models.load_model(MODEL_PATH)
    myModel.summary()
    files = os.listdir(TestFolder)
    badClasses = 0
    for file in files:
        data, myclass = readData(TestFolder + file)
        data = preprocessData(data)
        predictedClass = predict(myModel, data)
        if not myclass == predictedClass:
            badClasses+=1
            print(file)
    print("Misclassifications: ", badClasses)

if __name__ == "__main__":
    main()
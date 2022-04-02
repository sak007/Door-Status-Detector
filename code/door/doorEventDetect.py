import os
import time
import math
import json

import MPU6050
import MPU6050EventBuffer
from wiotpClient import DeviceClient

#from Button import Button

#from IOConfig import *

BATime = 1 # Amount of time to record data before and after open/close

MyFolder = "../../data/jppahl/"

# Looks at the filenames in a given directory to see if they match the formart
# data_#_#.csv to try to get the second #, which we consider to be the file id
# to get the next available id for the next file
def getStartingId(folder):
    myid = 0
    hFile = "N/A"
    files = os.listdir(MyFolder)
    if len(files) > 0:
        for file in files: # Check filenames
            sections = file[:-4].split("_") # Cut off last 4 chars corresponding to .csv and split by _
            if len(sections) == 3 and int(sections[-1]) > myid: # look at the id field
                hFile = file
                myid = int(sections[-1])
    return myid

def addTrainingDataset(data, channels, motionStartPoint, motionEndPoint, sampleRate, aRange, gRange):
    avgGx = sum(data[channels[3]])/len(data[channels[3]])
    maxGx = max(data[channels[3]])
    minGx = min(data[channels[3]])

    print("Avg Gx: " + str(avgGx) + ", Min Gx: " + str(minGx) + ", Max Gx: "  + str(maxGx))

    # Trying to auto classify the events for training purposes.
    # If the average Gx in the of the events is positive (above
    # a threshold) and we don't see a 'large' negative Gx data
    # point then assume it was an open event, the same logic
    # in reverse is a close event. The reason we are looking for
    # a large data point in the opposite direction of the
    # average is to try an avoid classifying an open and close
    # event as either simply and open or a close.
    if avgGx > 5:
        if minGx > -5:
            myclass = "o" # Open event
        else:
            myclass = "u" # Unknown event
    elif avgGx < -5:
        if maxGx < 5:
            myclass = "c" # Close event
        else:
            myclass = "u" # Unknown event
    else:
        myclass = "u" # Unknown event

    myid = getStartingId(MyFolder) + 1
    filename = "data_" + myclass + "_" + str(myid) + ".csv"
    data2 = {"ax":[],"ay":[],"az":[],"gx":[],"gy":[],"gz":[]}
    with open(MyFolder + filename, "w") as f:
        f.write("info,\n")
        f.write("sampleRate, " + str(sampleRate) + ",\n")
        f.write("aRange, " + str(aRange) + ",\n")
        f.write("gRange, " + str(gRange) + ",\n")
        f.write("start," + str(motionStartPoint) + ",\n")
        f.write("stop," + str(motionEndPoint) + ",\n")
        for key in data:
            f.write(key + ",")
            for i, val in enumerate(data[key]):
                data2[key].append(val)
                f.write(str(val) + ",")
            f.write("\n")
    print("Wrote Event: " + filename)

def main():

    f = open('../../properties.json')
    properties = json.load(f)
    DOOR_MODE = properties['DOOR_MODE']
    DOOR_TRAIN_FOLDER = properties['DOOR_TRAIN_FOLDER']

    # Sensor Settings
    sampleRate = 100
    aRange = 2
    gRange = 250
    # Expected sample rate based on our settings
    expectedSampleRate = MPU6050.expectedSampleRate(sampleRate)
    # Initilaize the sensor and buffer
    sensor = MPU6050.MPU6050(sampleRate=sampleRate, aRange=aRange, gRange=gRange)
    eventBuffer = MPU6050EventBuffer.MPU6050EventBuffer(1.5,2,10,0.200,0.500,sensor)

    print("Initalizing Event Buffer...")
    eventBuffer.start()
    while eventBuffer.isCalibratedFlag() == False:
        continue
    print("Buffer Initalization Complete.")

    if DOOR_MODE != "train":
        client = DeviceClient()
        print("Event monitoring ready, capturing events for classification.")
    else: 
        print("Event monitoring ready, capturing events for training.")

    while True:
        if eventBuffer.checkForEvent() == True:
            data = {"ax":[],"ay":[],"az":[],"gx":[],"gy":[],"gz":[]}
            channels = list(data.keys())
            # Extract data from the buffer and organize it by channel
            numPoints = eventBuffer.bufferLen()
            print("Num Points:" + str(numPoints))

            for i in range(numPoints):
                chunk = eventBuffer.read()
                for j, val in enumerate(chunk): # For each channel
                    data[channels[j]].append(val)

            motionStartPoint = eventBuffer.getEventStartPoint()
            motionEndPoint = eventBuffer.getEventEndPoint()

            if DOOR_MODE == "train":
                addTrainingDataset(data, channels, motionStartPoint, motionEndPoint, sampleRate, aRange, gRange)
            else:
                for e in data.keys():
                    data[e] = data[e][motionStartPoint:motionEndPoint]
                client.publish('imu', data)

            eventBuffer.clearEvent()

if __name__ == "__main__":
    main()

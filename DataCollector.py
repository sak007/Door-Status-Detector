import os
import time
import math

import matplotlib.pyplot as plt

import MPU6050
import MPU6050Buffer
from Button import Button

from IOConfig import *

BATime = 1 # Amount of time to record data before and after open/close
# data_0_0.csv

MyFolder = "data/radek/"

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
    print(myid, hFile)
    return myid

def main():
    # Get last used file id
    myid = getStartingId(MyFolder)
    # Sensor Settings
    sampleRate = 100
    aRange = 2
    gRange = 250
    # Expected sample rate based on our settings
    expectedSampleRate = MPU6050.expectedSampleRate(sampleRate) 
    # Initilaize the sensor and buffer
    sensor = MPU6050.MPU6050(sampleRate=sampleRate, aRange=aRange, gRange=gRange)
    buf = MPU6050Buffer.MPU6050Buffer(sensor)
    # Buffer trigger button
    setup()
    oBtn = Button(DOOR_OPENED) # Detect when the door finished opening
    cBtn = Button(DOOR_CLOSED) # Detect when the door finished closing

    if oBtn.isOn(): # Door is open
        myclass = 1  # closing it
        print("Opening a door")
    elif cBtn.isOn(): # Door is closed
        myclass = 0 # opening it
        print("Closing a door")
    else:
        raise Exception("Make sure the door is either open or closed")
    
    state = 0
    armTime = time.time()
    buf.start()
    time.sleep(BATime)
    print("Armed")
    while state == 0:
        # Wait until the contact sensor releases
        if myclass == 0 and not cBtn.isOn() or \
            myclass == 1 and not oBtn.isOn():
            startTime = time.time()
            state = 1
            print("Motion Detected")
            break
        time.sleep(.005)
    while state == 1:
        # Wait until the other contact sensor goes live
        if myclass == 0 and oBtn.isOn() or \
            myclass == 1 and cBtn.isOn():
            endTime = time.time()
            print("Contact Detected")
            time.sleep(BATime)
            buf.stop(True)
            bufferStopTime = time.time()
            break
        time.sleep(.005)

    time.sleep(1)
    motionStartTime = startTime - armTime
    bufferTime = bufferStopTime - armTime
    motionTime = endTime - startTime 
    # Read the data from the buffer
    numPoints = buf.bufferLen()
    actualSampleRate = numPoints / bufferTime
    startPoint = math.floor(motionStartTime * actualSampleRate)
    print("Start Point ", startPoint)
    print("Total # of points: ", numPoints)
    print("Runtimes (Buffer, Motion): {:.2f}s\t{:.2f}s".format(bufferTime, motionTime ))
    print("Sample Rates (Requested, Expected, Mean): {:d}Hz    {:.2f}Hz    {:.2f}Hz".format( 
        sampleRate, expectedSampleRate, actualSampleRate))
    data = {"ax":[],"ay":[],"az":[],"gx":[],"gy":[],"gz":[]}
    channels = list(data.keys())
    # Extract data from the buffer and organize it by channel
    for i in range(numPoints):
        chunk = buf.read()
        for j, val in enumerate(chunk): # For each channel
            data[channels[j]].append(val)

    # Estimate which samples motion occured and stopped
    dataStorePoint = startPoint - math.floor(actualSampleRate * BATime)
    motionStartPoint = math.floor(actualSampleRate * BATime)
    motionEndPoint = math.floor(numPoints - startPoint + BATime * actualSampleRate)
    print("Motion between points: ", motionStartPoint, motionEndPoint)
    # Save the data
    myid += 1
    filename = "data_" + str(myclass) + "_" + str(myid) + ".csv"
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
                if i < dataStorePoint:
                    continue
                data2[key].append(val)
                f.write(str(val) + ",")
            f.write("\n")
    
    plot = True
    if plot:
        channel = "ax"
        endPoint = numPoints - math.floor(BATime * actualSampleRate)
        plt.figure()
        x1 = list(range(0, numPoints))
        x2 = list(range(dataStorePoint, numPoints))
        plt.plot(x1, data[channel],  label = "All Data")
        plt.plot(x2, data2[channel], label = "Motion+")
        plt.axvline(x=startPoint, color = "k")
        plt.axvline(x=endPoint, color = "k")
        plt.legend()
        plt.show()
    GPIO.cleanup()
    
if __name__ == "__main__":
    main()
    
    


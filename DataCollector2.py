import RPi.GPIO as GPIO
import os
import time
import math

import matplotlib.pyplot as plt

import MPU6050
import MPU6050Buffer
from Button import Button

from IOConfig import *
# + Signal is opening
# - is closing
# 0 is  closing
# 1 is opening
BATime = 1.5 # Amount of time to record data before and after open/close
GPIO.setmode(GPIO.BOARD)
# data_0_0.csv

MyFolder = "data/radek/"
#MyFolder = "data/debug/"

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
    setup()
    GPIO.output(READY_LED, GPIO.LOW)
    oBtn = Button(DOOR_OPENED) # Detect when the door finished opening
    cBtn = Button(DOOR_CLOSED) # Detect when the door finished closing
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
    


    trials = 50
    for k in range(trials):
        print("TRIAL: ", k)
        if oBtn.isOn(): # Door is open
            myclass = 1  # closing it
            print("Opening a door")
        elif cBtn.isOn(): # Door is closed
            myclass = 0 # opening it
            print("Closing a door")
        else:
            raise Exception("Make sure the door is either open or closed")

        armTime = time.time()
        if k == 0:
            buf.start()
        else:
            buf.startBuffering()
        time.sleep(BATime)
        print("Armed")
        GPIO.output(READY_LED, GPIO.HIGH)
        # Wait until the contact sensor releases
        if myclass == 0:
            GPIO.wait_for_edge(cBtn.pin,GPIO.FALLING)
            startTime = time.time() - .8
            print("c")
        elif myclass == 1:
            GPIO.wait_for_edge(oBtn.pin, GPIO.FALLING)
            startTime = time.time() - .35
            print("d")
        else:
            raise Exception()
        
        time.sleep(.25)
        print("Motion Detected")
        # Wait until the other contact sensor goes live
        GPIO.output(READY_LED, GPIO.LOW)
        if myclass == 0:
            GPIO.wait_for_edge(oBtn.pin,GPIO.RISING)
            print("a")
            time.sleep(.45)
        elif myclass == 1:
            GPIO.wait_for_edge(cBtn.pin, GPIO.RISING)
            print("b")
            time.sleep(1.15)
        else:
            raise Exception()
            
        endTime = time.time()
        print("Contact Detected")
        time.sleep(BATime)
        buf.stopBuffering()
        bufferStopTime = time.time()

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
        dataStorePoint2 = numPoints - dataStorePoint - motionStartPoint
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
            f.write("stop," + str(dataStorePoint2) + ",\n")
            #f.write("stop," + str(motionEndPoint) + ",\n")
            for key in data:
                f.write(key + ",")
                for i, val in enumerate(data[key]):
                    if i < dataStorePoint:
                        continue
                    data2[key].append(val)
                    f.write(str(val) + ",")
                f.write("\n")
        
        plot = False
        if plot:
            channel = "gx"
            endPoint = numPoints - math.floor(BATime * actualSampleRate)
            plt.figure()
            plt.title(channel)
            x1 = list(range(0, numPoints))
            x2 = list(range(dataStorePoint, numPoints))
            plt.plot(x1, data[channel],  label = "All Data")
            plt.plot(x2, data2[channel], label = "Motion+")
            plt.axvline(x=startPoint, color = "k")
            plt.axvline(x=endPoint, color = "k")
            plt.legend()
            plt.show()
    GPIO.cleanup()
    buf.stop(True)
    print("end")
    
if __name__ == "__main__":
    main()
    
    


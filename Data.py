import matplotlib.pyplot as plt
import os
import numpy as np
import random

MyFolder = "data/radek/"
channels = ["ax", "ay", "az", "gx", "gy", "gz"]

# Looks at the filenames in a given directory to see if they match the formart
# data_#_#.csv to try to get the first #, which we consider to be the classification
# 0 for opening, 1 for closing
def getClass(file):
    return int(file[:-4].split("_")[1])

def readFile(file):
    data = {}
    with open(file, "r") as f:
        lines = f.readlines()
        data["sampleRate"] = int(lines[1].split(",")[1])
        data["aRange"] = int(lines[2].split(",")[1])
        data["gRange"] = int(lines[3].split(",")[1])
        data["start"] = int(lines[4].split(",")[1])
        data["stop"] = int(lines[5].split(",")[1])
        # 6 Channel signals
        for line in lines[6:13]:
            line = line.split(',')
            key = line[0]
            data[key] = []
            # Get all the data points for the channel
            for val in line[1:]:
                if val != "\n":
                    data[key].append(float(val))
    data["x"] = list(range(0, len(data["ax"])))
    data["class"] = getClass(file)
    return data


# Normalizes data by subtracting the mean and dividing by the standard deviation 
def normalize(data):
    mean = np.mean(data,axis=0)
    sd = np.std(data, axis=0)
    data2 = (data - mean) / sd
    return data2

# Normalize each of the signals
def normailizeData(data):
    for channel in channels:
        data[channel] = normalize(data[normailizeData])
    return data

def getRandomInts(start, end, numVals):
    vals = list(range(start, end))
    randomVals = random.sample(vals, numVals)
    randomVals.sort(reverse=True)
    return randomVals

def splitList(mylist, indexes):
    mylist2 = []
    for index in indexes:
        mylist2.append(mylist.pop(index))
    return mylist, mylist2

def plotStartStop(data):
    plt.axvline(x=data["start"], color="k")
    plt.axvline(x=data["stop"], color = "k")

def downsample(data, factor):
    data2 = {}
    data2["sampleRate"] = data["sampleRate"]
    data2["aRange"] =  data["aRange"]
    data2["gRange"] = data["gRange"]
    data2["start"] = data["start"]
    data2["stop"] = data["stop"] 
    channels =list(data.keys())[5:11]
    for channel in channels:
        data2[channel] = []
        for i,val in enumerate(data[channel]):
            if i % factor == 0:
                data2[channel].append(val)
    data2["x"] = list(range(0, len(data["ax"]), factor))
    return data2

def plot6(data, title):
    x = data["x"]
    plt.figure()
    plt.suptitle(title)
    plt.subplot(3,2,1)
    plt.plot(x, data["ax"], label = "Ax")
    plt.legend()
    plotStartStop(data)
    plt.subplot(3,2,3)
    plt.plot(x, data["ay"], label = "Ay")
    plt.legend()
    plotStartStop(data)
    plt.subplot(3,2,5)
    plt.plot(x, data["az"], label = "Az")
    plt.legend()
    plotStartStop(data)
    plt.subplot(3,2,2)
    plt.plot(x, data["gx"], label = "Gx")
    plt.legend()
    plotStartStop(data)
    plt.subplot(3,2,4)
    plt.plot(x, data["gy"], label = "Gy")
    plt.legend()
    plotStartStop(data)
    plt.subplot(3,2,6)
    plt.plot(x, data["gz"], label = "Gz")
    plotStartStop(data)
    plt.legend()


def main():
    files = os.listdir(MyFolder)
    counts = [0,0]
    for file in files:
        counts[getClass(file)] += 1
    print("Opening: ", counts[0])
    print("Closing: ", counts[1])

    i = 10
    file = MyFolder + files[i]
    data = readFile(file)
    data2 = downsample(data, 2)
    print("Sample Rate: ", data["sampleRate"])
    plot6(data, files[i])
    plot6(data2, files[i] + " downsampled")
    plt.show()

if __name__ == "__main__":
    main()
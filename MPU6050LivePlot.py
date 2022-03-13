import time
from matplotlib import pyplot as plt
import numpy as np

import MPU6050
import MPU6050Buffer

def shiftAndInsert(arr, val):
    if len(val) < len(arr):
        arr[0:len(arr) - len(val)] = arr[len(val):]
        arr[len(arr) - len(val):] = val
    else:
        return val[len(val)-len(arr):]
    return arr



def main():
    sampleRate = 25
    gRange = 250 # degrees/s
    aRange = 2 # gs
    # Start the sensor and buffer
    sensor = MPU6050.MPU6050(sampleRate=sampleRate, gRange=gRange, aRange=aRange)
    buf = MPU6050Buffer.MPU6050Buffer(sensor)
    timeToDisplay = 8
    numPoints = sampleRate*timeToDisplay
    x = np.linspace(timeToDisplay, 0, num=numPoints) # Preallocate 100 size array
    fig = plt.figure()
    ax1 = fig.add_subplot(3, 1, 1)
    plt.title("Accelerometers")
    ax2 = fig.add_subplot(3, 1, 2)
    plt.ylabel("g")
    ax3 = fig.add_subplot(3, 1, 3)
    plt.xlabel("Time since now (s)")
    accelX = np.zeros(numPoints)
    accelY = np.zeros(numPoints)
    accelZ = np.zeros(numPoints)

    line1, = ax1.plot([], lw=3)
    line2, = ax2.plot([], lw=3)
    line3, = ax3.plot([], lw=3)
    text = ax1.text(timeToDisplay - .2, aRange/2, "")

    # Set x and y axis limits
    ax1.set_xlim(x.max(), x.min())
    ax1.set_ylim([-1*aRange, aRange])
    ax2.set_xlim(x.max(), x.min())
    ax2.set_ylim([-1*aRange, aRange])
    ax3.set_xlim(x.max(), x.min())
    ax3.set_ylim([-1*aRange, aRange])

    fig.canvas.draw()   # note that the first draw comes before setting data 

    # Cache backgrounds
    ax1background = fig.canvas.copy_from_bbox(ax1.bbox)
    ax2background = fig.canvas.copy_from_bbox(ax2.bbox)
    ax3background = fig.canvas.copy_from_bbox(ax3.bbox)
    plt.show(block=False)
    time.sleep(1)


    print("Starting")
    buf.start()
    t_start = time.time()
    # for i in np.arange(1000):
    i=0
    while True:
        # Read the new points from the buffer
        numPoints = buf.bufferLen()
        newPoints = [[],[],[]]
        for j in range(numPoints):
            a = buf.read()
            newPoints[0].append(a[0])
            newPoints[1].append(a[1])
            newPoints[2].append(a[2])
        # Shift the old data points and insert the new ones
        accelX = shiftAndInsert(accelX, newPoints[0])
        accelY = shiftAndInsert(accelY, newPoints[1])
        accelZ = shiftAndInsert(accelZ, newPoints[2])  
            
        line1.set_data(x, accelX)
        line2.set_data(x, accelY)
        line3.set_data(x, accelZ)
        i+=1
        #tx = 'Mean Frame Rate:\n {fps:.3f}FPS'.format(fps= ((i) / (time.time() - t_start)) ) 
        tx = '{fps:.3f}FPS'.format(fps= ((i) / (time.time() - t_start)))
        text.set_text(tx)

        # restore background
        fig.canvas.restore_region(ax1background)
        fig.canvas.restore_region(ax2background)
        fig.canvas.restore_region(ax3background)

        # redraw just the points
        ax1.draw_artist(line1)
        ax2.draw_artist(line2)
        ax3.draw_artist(line3)
        ax1.draw_artist(text)

        # fill in the axes rectangle
        fig.canvas.blit(ax1.bbox)
        fig.canvas.blit(ax2.bbox)
        fig.canvas.blit(ax3.bbox)

        # Update
        fig.canvas.flush_events()
    # time.sleep(10)




    #buf.stop()



if __name__ == "__main__":
    main()

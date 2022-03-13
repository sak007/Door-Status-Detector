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
    sampleRate = 50
    gRange = 500 # degrees/s
    aRange = 2 # gs
    # Start the sensor and buffer
    sensor = MPU6050.MPU6050(sampleRate=sampleRate, gRange=gRange, aRange=aRange)
    buf = MPU6050Buffer.MPU6050Buffer(sensor)
    timeToDisplay = 10
    numPoints = sampleRate*timeToDisplay
    print(numPoints)
    x = np.linspace(timeToDisplay, 0, num=numPoints) # Preallocate 100 size array

    # Accel Figure
    fig1 = plt.figure(figsize=(10,5))
    ax1 = fig1.add_subplot(3, 2, 1)
    plt.title("Accelerometers")
    ax2 = fig1.add_subplot(3, 2, 3)
    plt.ylabel("g")
    ax3 = fig1.add_subplot(3, 2, 5)
    plt.xlabel("Time since now (s)")
    ax4 = fig1.add_subplot(3, 2, 2)
    plt.title("Gyroscope")
    ax5 = fig1.add_subplot(3, 2, 4)
    plt.ylabel("degrees/s")
    ax6 = fig1.add_subplot(3, 2, 6)
    plt.xlabel("Time since now (s)")

    accelX = np.zeros(numPoints)
    accelY = np.zeros(numPoints)
    accelZ = np.zeros(numPoints)
    gyroX = np.zeros(numPoints)
    gyroY = np.zeros(numPoints)
    gyroZ = np.zeros(numPoints)

    line1, = ax1.plot([], lw=3)
    line2, = ax2.plot([], lw=3)
    line3, = ax3.plot([], lw=3)
    text = ax1.text(timeToDisplay - .2, aRange*.65, "")
    line4, = ax4.plot([], lw=3)
    line5, = ax5.plot([], lw=3)
    line6, = ax6.plot([], lw=3)

    # Set x and y axis limits
    ax1.set_xlim(x.max(), x.min())
    ax1.set_ylim([-1*aRange, aRange])
    ax2.set_xlim(x.max(), x.min())
    ax2.set_ylim([-1*aRange, aRange])
    ax3.set_xlim(x.max(), x.min())
    ax3.set_ylim([-1*aRange, aRange])
    ax4.set_xlim(x.max(), x.min())
    ax4.set_ylim([-1*gRange, gRange])
    ax5.set_xlim(x.max(), x.min())
    ax5.set_ylim([-1*gRange, gRange])
    ax6.set_xlim(x.max(), x.min())
    ax6.set_ylim([-1*gRange, gRange])

    # Cache backgrounds
    ax1background = fig1.canvas.copy_from_bbox(ax1.bbox)
    ax2background = fig1.canvas.copy_from_bbox(ax2.bbox)
    ax3background = fig1.canvas.copy_from_bbox(ax3.bbox)
    ax4background = fig1.canvas.copy_from_bbox(ax4.bbox)
    ax5background = fig1.canvas.copy_from_bbox(ax5.bbox)
    ax6background = fig1.canvas.copy_from_bbox(ax6.bbox)

    fig1.canvas.draw()   # note that the first draw comes before setting data 

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
        newPoints = [[],[],[],[],[],[]]
        for j in range(numPoints):
            a = buf.read()
            newPoints[0].append(a[0])
            newPoints[1].append(a[1])
            newPoints[2].append(a[2])
            newPoints[3].append(a[3])
            newPoints[4].append(a[4])
            newPoints[5].append(a[5])
        # Shift the old data points and insert the new ones
        accelX = shiftAndInsert(accelX, newPoints[0])
        accelY = shiftAndInsert(accelY, newPoints[1])
        accelZ = shiftAndInsert(accelZ, newPoints[2])  
        gyroX = shiftAndInsert(gyroX, newPoints[3])
        gyroY = shiftAndInsert(gyroY, newPoints[4])
        gyroZ = shiftAndInsert(gyroZ, newPoints[5])  
            
        line1.set_data(x, accelX)
        line2.set_data(x, accelY)
        line3.set_data(x, accelZ)
        line4.set_data(x, gyroX)
        line5.set_data(x, gyroY)
        line6.set_data(x, gyroZ)
        i+=1
        #tx = 'Mean Frame Rate:\n {fps:.3f}FPS'.format(fps= ((i) / (time.time() - t_start)) ) 
        tx = '{fps:.3f}FPS, '.format(fps= ((i) / (time.time() - t_start))) + str(numPoints)
        text.set_text(tx)

        # restore background
        fig1.canvas.restore_region(ax1background)
        fig1.canvas.restore_region(ax2background)
        fig1.canvas.restore_region(ax3background)
        fig1.canvas.restore_region(ax4background)
        fig1.canvas.restore_region(ax5background)
        fig1.canvas.restore_region(ax6background)

        # redraw just the points
        ax1.draw_artist(line1)
        ax2.draw_artist(line2)
        ax3.draw_artist(line3)
        ax1.draw_artist(text)
        ax4.draw_artist(line4)
        ax5.draw_artist(line5)
        ax6.draw_artist(line6)

        # fill in the axes rectangle
        fig1.canvas.blit(ax1.bbox)
        fig1.canvas.blit(ax2.bbox)
        fig1.canvas.blit(ax3.bbox)
        fig1.canvas.blit(ax4.bbox)
        fig1.canvas.blit(ax5.bbox)
        fig1.canvas.blit(ax6.bbox)

        # Update
        fig1.canvas.flush_events()
    # time.sleep(10)




    #buf.stop()



if __name__ == "__main__":
    main()

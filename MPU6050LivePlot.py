import time
from matplotlib import pyplot as plt
import numpy as np

import MPU6050
import MPU6050Buffer

def shiftAndInsert(arr, val):
    arr[0:len(arr) - len(val)] = arr[len(val):]
    arr[len(arr) - len(val):] = val
    return arr
    #arr = np.delete(arr, 0)
    #return np.append(arr, val)


def main():
    sampleRate = 25
    timeToDisplay = 4
    x = np.linspace(timeToDisplay, 0, num=100) # Preallocate 100 size array
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    y = np.zeros(100)

    line, = ax1.plot([], lw=3)
    text = ax1.text(1,1.6, "")

    # Set x and y axis limits
    ax1.set_xlim(x.max(), x.min())
    ax1.set_ylim([-2, 2])

    fig.canvas.draw()   # note that the first draw comes before setting data 

    # cache the background
    ax1background = fig.canvas.copy_from_bbox(ax1.bbox)

    plt.show(block=False)

    t_start = time.time()

    line.set_data(x, y) # sine wave update
    #line.set_data(x, np.sin(x/3.+k)) # sine wave update

    # restore background
    fig.canvas.restore_region(ax1background)

    # redraw just the points
    ax1.draw_artist(line)
    ax1.draw_artist(text)

    # fill in the axes rectangle
    fig.canvas.blit(ax1.bbox)

    fig.canvas.flush_events()

    # Basically, we recompute the full sinewave each time, but we increment k whic effectivly adds
    # one point to the plot
    sensor = MPU6050.MPU6050()
    buf = MPU6050Buffer.MPU6050Buffer(sensor)
    buf.start()
    for i in np.arange(1000):
        points = buf.bufferLen()
        data = []
        for j in range(points):
            a = buf.read()[0]
            data.append(a)
        y = shiftAndInsert(y, data)

            
        # a = sensor.readLive()[0]
        # print(a)
            #y = shiftAndInsert(y, a)

        line.set_data(x, y) # sine wave update
        #line.set_data(x, np.sin(x/3.+k)) # sine wave update
        tx = 'Mean Frame Rate:\n {fps:.3f}FPS'.format(fps= ((i+1) / (time.time() - t_start)) ) 
        text.set_text(tx)

        # restore background
        fig.canvas.restore_region(ax1background)

        # redraw just the points
        ax1.draw_artist(line)
        ax1.draw_artist(text)

        # fill in the axes rectangle
        fig.canvas.blit(ax1.bbox)

        fig.canvas.flush_events()
    time.sleep(10)




    #buf.stop()



if __name__ == "__main__":
    main()

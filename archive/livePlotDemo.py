import time
from matplotlib import pyplot as plt
import numpy as np
# Taken from https://stackoverflow.com/questions/40126176/fast-live-plotting-in-matplotlib-pyplot

# Test to see if your pi can run live plotting

def liveUpdateDemo():
    x = np.linspace(0,50., num=100) # Preallocate 100 size array
    X,Y = np.meshgrid(x,x) # 100 by 100 mesh grid
    fig = plt.figure()
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)

    img = ax1.imshow(X, vmin=-1, vmax=1, interpolation="None", cmap="RdBu")

    line, = ax2.plot([], lw=3)
    text = ax2.text(0.8,0.5, "")

    # Set x and y axis limits
    ax2.set_xlim(x.min(), x.max())
    ax2.set_ylim([-1.1, 1.1])

    fig.canvas.draw()   # note that the first draw comes before setting data 

    # cache the background
    axbackground = fig.canvas.copy_from_bbox(ax1.bbox)
    ax2background = fig.canvas.copy_from_bbox(ax2.bbox)

    plt.show(block=False)

    t_start = time.time()
    k=0.

    # Basically, we recompute the full sinewave each time, but we increment k whic effectivly adds
    # one point to the plot
    for i in np.arange(1000):
        img.set_data(np.sin(X/3.+k)*np.cos(Y/3.+k)) # mesh grid update
        line.set_data(x, np.sin(x/3.+k)) # sine wave update
        tx = 'Mean Frame Rate:\n {fps:.3f}FPS'.format(fps= ((i+1) / (time.time() - t_start)) ) 
        text.set_text(tx)
        #print tx
        k+=0.11
        # restore background
        fig.canvas.restore_region(axbackground)
        fig.canvas.restore_region(ax2background)

        # redraw just the points
        ax1.draw_artist(img)
        ax2.draw_artist(line)
        ax2.draw_artist(text)

        # fill in the axes rectangle
        fig.canvas.blit(ax1.bbox)
        fig.canvas.blit(ax2.bbox)

        fig.canvas.flush_events()


if __name__ == "__main__":
    liveUpdateDemo()   

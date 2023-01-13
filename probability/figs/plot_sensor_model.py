import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import matplotlib
matplotlib.rcParams['text.usetex'] = True

import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 8})
np.set_printoptions(precision=3, suppress=True)

def plot_dist(p_x, name, ylabel, hide_y=False):
    num_spots = len(p_x)
    x = np.linspace(1., num_spots, num_spots)
    fig = plt.figure(figsize=(1.75, 1.25))
    ax = fig.gca()
    ax.bar(x, p_x, width=1.0, color=(.5,.5,.7), edgecolor='black')
    #ax.set_xlabel('position')
    ax.set_ylim(0, 1.1)
    ax.set_xticks([1, 10])
    ax.set_ylabel(ylabel)
    ax.set_xlabel('$X$')
    
    fig.tight_layout(pad=0.1)
    if hide_y:
        ax.set_ylabel('')
    #if hide_y:
    #    ax.get_yaxis().set_visible(False)
    
    fig.savefig(name)


p_x = np.arange(0, 10)
p_x = 1/ 2 ** np.abs(p_x - 4)
plot_dist(p_x, 'sensor_true.pdf', '$P(Z=True \mid X)$')
p_x = np.arange(0, 10)
p_x = 1 - 1/ 2 ** np.abs(p_x - 4)
plot_dist(p_x, 'sensor_false.pdf', '$P(Z=False \mid X)$')

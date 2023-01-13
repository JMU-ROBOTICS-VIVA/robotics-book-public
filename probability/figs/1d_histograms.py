import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import scipy.stats as stats

import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 8})
np.set_printoptions(precision=3, suppress=True)
matplotlib.rcParams['text.usetex'] = True


def plot_dist(p_x, name, hide_y=False):
    p_x = p_x  /np.sum(p_x)
    print(p_x)
    num_spots = len(p_x)
    x = np.linspace(1., num_spots, num_spots)
    fig = plt.figure(figsize=(1.75, 1.25))
    ax = fig.gca()
    ax.bar(x, p_x, width=1.0, color='gray', edgecolor='black')
    #ax.set_xlabel('position')
    ax.set_ylim(0, 1.1)
    ax.set_xticks([1, 10])
    ax.set_ylabel('$P(X)$')
    
    fig.tight_layout(pad=0.1)
    if hide_y:
        ax.set_ylabel('')
    #if hide_y:
    #    ax.get_yaxis().set_visible(False)
    
    fig.savefig(name)



p_x = np.ones(10)
plot_dist(p_x, 'uniform_hist.pdf')

p_x = np.zeros(10)
p_x[0] = 1.0
plot_dist(p_x, 'certain_hist.pdf', True)


x = np.linspace(1., 10, 10)
p_x = stats.norm.pdf(x, 5.0, 1.0)
plot_dist(p_x, 'gauss_hist.pdf', True)



p_x = np.zeros(10)
p_x[0:5] = 1.0
plot_dist(p_x, 'left_hist.pdf', False)



# the histogram of the data






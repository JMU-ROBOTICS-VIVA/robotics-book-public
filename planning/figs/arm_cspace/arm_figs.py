""" Generate figures for the robot arm. 

Author: Nathan Sprague

"""


import shapely.geometry

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches
import matplotlib.transforms
from matplotlib import rc
from arm import Arm

from arm_plotting import draw_c_space, draw_c_space_torus, draw_world

rc('text', usetex=True)

# Set default arm characteristics for examples and figures.
L1 = 100.0
L2 = 100.0
LINK_WIDTH = 6
OBSTACLES = []
#OBSTACLES.append(shapely.geometry.box(-120, 110, -60, 170))
#OBSTACLES.append(shapely.geometry.Point(30, -100).buffer(40)) # circle
OBSTACLES.append(shapely.geometry.box(-150, 60, -90, 120))
OBSTACLES.append(shapely.geometry.Point(90, -40).buffer(40)) # circle
OBSTACLE_COLORS = [(1., .5, .5), (.5, .5, 1), (.5, 1, .5)]


def save_figures():
    matplotlib.rcParams['lines.linewidth'] = .5 
    matplotlib.rcParams['patch.linewidth'] = .5 
    fig = plt.figure(figsize=(2, 2), frameon=False)
    ax = fig.gca()
    arm = Arm((L1, L2), (LINK_WIDTH, LINK_WIDTH))
    figsize = (2.4,2.4)
    
    draw_world(arm, ax, 45, 90, OBSTACLES, OBSTACLE_COLORS, False, True)

    fig.set_size_inches(*figsize)
    plt.savefig('arm_diagram.pdf', format="pdf", bbox_inches=None)
    plt.show()

    fig = plt.figure(figsize=figsize, frameon=False)
    ax = fig.gca()
    matplotlib.rcParams['patch.linewidth'] = .2
    matplotlib.rcParams['lines.markersize'] = 1
    draw_world(arm, ax,  45, 90, OBSTACLES, OBSTACLE_COLORS, True, False)
    ax.text(OBSTACLES[0].centroid.x,
            OBSTACLES[0].centroid.y,
            "$\mathcal{O}_1$",
            horizontalalignment='center',
            verticalalignment='center')
    ax.text(OBSTACLES[1].centroid.x,
            OBSTACLES[1].centroid.y,
            "$\mathcal{O}_2$",
            horizontalalignment='center',
            verticalalignment='center')
    ax.annotate("$\mathcal{A}(\mathbf{q})$",
                xytext=(-60,66),
                xy=(33, 106),
                arrowprops=dict(arrowstyle="-|>",
                                facecolor="black",
                                shrinkA=0,
                                shrinkB=0)) 
    ax.annotate("$\mathcal{A}(\mathbf{q})$",
                xytext=(-60,66),
                xy=(33, 33),
                arrowprops=dict(arrowstyle="-|>",
                                facecolor="black",
                                shrinkA=0, 
                                shrinkB=0)) 
    lim = (L1 + L2) * .9
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)

    fig.set_size_inches(*figsize)
    plt.savefig('arm_world.pdf', format="pdf", bbox_inches=None)
    plt.show()

    fig = plt.figure(figsize=figsize, frameon=False)
    ax = plt.axes(projection = '3d')
    draw_c_space_torus(ax, arm, OBSTACLES, OBSTACLE_COLORS)
    fig.set_size_inches(*figsize)
    plt.savefig('arm_torus.pdf', format="pdf", bbox_inches=None)
    plt.show()

    fig = plt.figure(figsize=figsize, frameon=False)
    ax = fig.gca()
    draw_c_space(arm, ax, OBSTACLES, OBSTACLE_COLORS)
    fig.tight_layout()
    fig.set_size_inches(*figsize)
    plt.savefig('arm_c_space.pdf', format="pdf", bbox_inches=None)
    plt.show()


def motion_figs():
    fig = plt.figure(figsize=(2, 2))
    ax = fig.gca()
    arm = Arm((L1, L2), (LINK_WIDTH, LINK_WIDTH))

    start = (90, -45)
    end = (20, 0)
    
    theta1 = np.linspace(start[0], end[0], 6)
    theta2 = np.linspace(start[1], end[1], 6)
    matplotlib.rcParams['patch.linewidth'] = .2
    matplotlib.rcParams['lines.markersize'] = 1
    draw_world(arm, ax, theta1, theta2, OBSTACLES, OBSTACLE_COLORS,
               show_obstacles=True, show_angles=False)
    lim = (L1 + L2) *1
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    plt.savefig('arm_world_motion.pdf', format="pdf", bbox_inches='tight')

    fig = plt.figure(figsize=(2, 2))
    ax = fig.gca()
    draw_c_space(arm, ax, OBSTACLES, OBSTACLE_COLORS)
    ax.arrow(start[0], start[1], (end[0] - start[0]) * .9,
             (end[1] - start[1]) * .9 ,head_width=12, facecolor='k',
             length_includes_head=True)
    ax.plot([start[0], end[0]], [start[1], end[1]], 'k.', markersize=5)
    ax.text(start[0] + 15, start[1], "$\mathbf{q}_I$")
    ax.text(end[0], end[1]+15, "$\mathbf{q}_G$")
    plt.savefig('arm_c_space_motion.pdf', format="pdf", bbox_inches='tight')

    plt.show()


def main():
    save_figures()
    motion_figs()

if __name__ == "__main__":
    main()


""" Demo of the Linear Kalman Filter 

Author: Nathan Sprague
Version: 2/2013
"""

import kalman
#import plot_gaussians
import draw_gaussians
import numpy as np
import matplotlib.pyplot as plt
import time

FIG_COUNT = 0

def stationaryKF():
    """ Build and return a Kalman filter object for tracking
    a stationary 2-d object """
    A =  np.array([[1., 0], # State transition matrix. (stationary 2d object)
                   [0., 1]])
    Q =  np.array([[.01, 0],  # Covariance of state transition noise.
                   [0., .01]])  # (object jitters)
    H = np.array([[1., 0], # Measurement model matrix (direct measurements)
                  [0., 1]])
    C_w =  np.array([[.3, 0],  # Covariance of sensor noise.
                     [0., .3]])
    x_0 = np.array([.5,.5]) # initial state estimate.
    P_0 =  np.eye(2) * 2. # initial Covariance estimate. 

    return kalman.KalmanFilter(A, Q, H, C_w, x_0, P_0)

def movingKF():
    """ Build and return a Kalman filter object for tracking
    a 2-D object moving at a fixed velocity """
    A =  np.array([[1., 0, .1, 0], # State transition matrix.
                   [0., 1, 0, .1],
                   [0., 0, 1, 0],
                   [0., 0, 0, 1]])
    Q =  np.array([[.1, 0, 0, 0],  # Covariance of state transition noise.
                   [0., .1, 0, 0],
                   [0., 0, .0, 0],
                   [0., 0, 0, .0]])
    H = np.array([[1., 0, 0, 0], 
                  [0., 1, 0, 0]])
    R =  np.array([[.1, 0],  # Covariance of sensor noise.
                   [0., .1]])
    x_0 = np.array([.2, .2, 8, 8]) # initial state estimate.
    P_0 =  np.eye(4) * .1 # initial Covariance estimate. 

    return kalman.KalmanFilter(A, Q, H, R, x_0, P_0)


def plot_without_sensor(kf, true_x, minx_plot, maxx_plot,
                        miny_plot, maxy_plot, title, linestyle="--"):
    global FIG_COUNT
    FIG_COUNT += 1
    draw_gaussians.confidence_ellipse(kf.x[0:2], kf.P[0:2,0:2], n_std=1.0, edgecolor='black',linestyle=linestyle)
    #true, = plt.plot(true_x[0], true_x[1], '*g')
    est, = plt.plot(kf.x[0], kf.x[1], 'sk')
    plt.xlim([minx_plot, maxx_plot])
    plt.ylim([miny_plot, maxy_plot])
    plt.title(title)
    #plt.legend([true, est], ['True Position', 'Estimated Position'])
    plt.axis('equal')
    
    plt.axis('off')
    plt.show()
    plt.draw()
    plt.savefig(f'pred_{FIG_COUNT}.svg', dpi=150)
    plt.ginput(timeout=-1)


def plot_with_sensor(kf, z, true_x, minx_plot, maxx_plot,
                        miny_plot, maxy_plot, title, show_ellipse=True):
    global FIG_COUNT
    FIG_COUNT += 1
    #plt.cla()
    if show_ellipse:
        draw_gaussians.confidence_ellipse(kf.x[0:2], kf.P[0:2,0:2], n_std=1.0, edgecolor='black')

    #true, = plt.plot(true_x[0], true_x[1], '*g')
    est, = plt.plot(kf.x[0], kf.x[1], 'sk')
    sens, = plt.plot(z[0], z[1], 'ob')
    plt.xlim([minx_plot, maxx_plot])
    plt.ylim([miny_plot, maxy_plot])
    #plt.legend([true, est, sens], ['True Position', 'Estimated Position', "Sensor Value"])
    plt.title(title)
    plt.axis('equal')
    plt.axis('off')
    plt.show()
    plt.draw()
    plt.savefig(f'correct_{FIG_COUNT}.svg', dpi=150)
    plt.ginput(timeout=-1)

def main(moving_target=True):
    """ 
    Loop through the predict/correct cycle, showing position estimates
    at each time step. 
    """
    
    minx_plot = 0
    maxx_plot = 4
    miny_plot = 0
    maxy_plot = 4

    if moving_target:
        kf = movingKF()
        true_x = np.array([.5, .5, 8., 8.])
    else:
        kf = stationaryKF()
        true_x = np.array([1,1])
        
    plt.ion()

    print("INITIAL STATE ESTIMATE.")
    plot_without_sensor(kf, true_x, minx_plot, maxx_plot, 
                        miny_plot, maxy_plot, "INITIAL STATE ESTIMATE", linestyle="-")

    for _ in range(1000):
        #plt.cla()

        # Move the object according to the transition model...
        true_x = (kf.A.dot(true_x) + 
                  np.random.multivariate_normal(np.zeros(true_x.shape), 
                                                kf.Q))

        # Generate a sensor reading according to the sensor model...
        z = kf.H.dot(true_x) + \
            np.random.multivariate_normal(np.array([0,0]),  kf.R)

        kf.predict()

        plot_without_sensor(kf, true_x, minx_plot, maxx_plot, 
                            miny_plot, maxy_plot, "AFTER PREDICTION")
        

        plot_with_sensor(kf, z, true_x, minx_plot, maxx_plot, 
                            miny_plot, maxy_plot, "SENSOR READING",show_ellipse=False)

        kf.correct(z)

        print("AFTER CORRECTION.")
        print(kf.x)
        print(kf.P)

        plot_with_sensor(kf, z, true_x, minx_plot, maxx_plot, 
                            miny_plot, maxy_plot, "AFTER CORRECTION")


if __name__ == "__main__":
    main()

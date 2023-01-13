""" Simple Linear Kalman Filter class. 

This implementation follows the description in 

An Introduction to the Kalman Filter (TR 95-041)
Greg Welch and Gary Bishop, 2006

Author: Nathan Sprague
Version: 2/2015
"""
import numpy as np


class KalmanFilter(object):
    """ Simple Kalman Filter Class. """

    def __init__(self, A, Q, H, R, x_0, P_0):
        """ Construct a Kalman Filter object. 

        Arguments:
           A - state transition matrix
           Q   - covariance matrix of the state transition function
           H - measurement model matrix
           R   - measurement covariance
           x_0 - initial state
           P_0 - initial state covariance matrix. 
        """

        self.A = A
        self.Q = Q
        self.H = H
        self.R = R
        self.x = x_0
        self.P = P_0

    def predict(self):
        """ 
        Perform one step of prediction based on the state transition model. 
        """
        
        # Project the state forward: (Equation 1.9)
        self.x = self.A.dot(self.x)
        # Update the state covariance: (Equation 1.10)
        self.P = self.A.dot(self.P).dot(self.A.T) + self.Q

    def correct(self, z):        
        """ 
        Update the state estimate with a sensor reading. 

        Arguments:
           z - measurement vector
        """
        
        # Compute the Kalman gain: (Equation 1.11)
        K_top = self.P.dot(self.H.T)
        K_bottom = self.H.dot(self.P).dot(self.H.T) + self.R
        K = K_top.dot(np.linalg.inv(K_bottom))
                   
        # Calculate the residual:
        r = z - self.H.dot(self.x)
        
        # Revise the state estimate: (Equation 1.12)
        self.x = self.x + K.dot(r)
        
        # Revise the state covariance: (Equation 1.13)
        self.P = (np.eye(self.P.shape[0]) - K.dot(self.H)).dot(self.P)



if __name__ == "__main__":
    pass

# Date: 06/01/2019
# Author: Callum Bruce
# Math helper module

import numpy as np

def transformationMatrix(referenceFrame1, referenceFrame2):
    """
    Transformation matrix for converting from referenceFrame1 to referenceFrame2

    Args:
        referenceFrame1 (object): referenceFrame1 object
        referenceFrame2 (object): referenceFrame2 object

    Returns:
        T (np.array): Transformation matrix to convert from referenceFrame1 to referenceFrame2
    """
    i = referenceFrame1.i
    j = referenceFrame1.j
    i_d = referenceFrame2.i
    j_d = referenceFrame2.j
    T = np.array([[np.dot(i,i_d),np.dot(j,i_d)],
                  [np.dot(j_d,i),np.dot(j,j_d)]])
    return T

def transformationMatrix3D(referenceFrame1, referenceFrame2):
    """
    Transformation matrix for converting from referenceFrame1 to referenceFrame2.

    Args:
        referenceFrame1 (object): referenceFrame1 object
        referenceFrame2 (object): referenceFrame2 object

    Returns:
        T (np.array): Transformation matrix to convert from referenceFrame1 to referenceFrame2
    """
    i = referenceFrame1.i
    j = referenceFrame1.j
    k = referenceFrame1.k
    i_d = referenceFrame2.i
    j_d = referenceFrame2.j
    k_d = referenceFrame2.k
    T = np.array([[np.dot(i,i_d), np.dot(j,i_d), np.dot(k,i_d)],
                  [np.dot(i,j_d), np.dot(j,j_d), np.dot(k,j_d)]
                  [np.dot(i,k_d), np.dot(j,k_d), np.dot(k,k_d)]])
    return T

def rotateVector(phi, theta, psi, vector):
    """
    Rotate 3D vector by phi (x), theta (y), psi (z):

    Args:
        phi (float): Rotation in x direction [deg]
        theta (float): Rotation in y direction [deg]
        psi (float): Rotation in z direction [deg]
        vector (list): List representing 3D vector to rotate i.e. [1, 0, 0]

    Returns:
        rotatedVector (list): 3D vector rotated by phi, theta, psi
    """
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(phi), -np.sin(phi)],
                   [0, np.sin(phi), np.cos(phi)]])

    Ry = np.array([[np.cos(theta), 0, np.sin(theta)],
                   [0, 1, 0],
                   [-np.sin(theta), 0, np.cos(theta)]])

    Rz = np.array([[np.cos(psi), -np.sin(psi), 0],
                   [np.sin(psi), np.cos(psi), 0],
                   [0, 0, 1]])

    R = np.matmul(Rz, np.matmul(Ry, Rx))
    '''
    R = np.array([[np.cos(psi)*np.cos(theta), np.cos(psi)*np.sin(theta)*np.sin(phi) - np.sin(psi)*np.cos(phi), np.cos(psi)*np.sin(theta)*np.cos(phi) + np.sin(psi)*np.sin(phi)],
                  [np.sin(psi)*np.cos(theta), np.sin(psi)*np.sin(theta)*np.sin(phi) + np.cos(psi)*np.cos(phi), np.sin(psi)*np.sin(theta)*np.cos(phi) - np.cos(psi)*np.sin(phi)],
                  [-np.sin(theta), np.cos(theta)*np.sin(phi), np.cos(theta)*np.cos(phi)]])
    '''
    rotatedVector = np.dot(R, vector)

    return rotateVector

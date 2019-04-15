# Date: 06/01/2019
# Author: Callum Bruce
# Math helper module

import numpy as np

def referenceFrames2rotationMatrix(referenceFrame1, referenceFrame2):
    """
    Rotation matrix for converting from referenceFrame1 to referenceFrame2.

    Args:
        referenceFrame1 (object): referenceFrame1 object.
        referenceFrame2 (object): referenceFrame2 object.

    Returns:
        R (np.array): Rotation matrix to convert from referenceFrame1 to
                      referenceFrame2.
    """
    i, j, k = referenceFrame1.getIJK()

    i_d, j_d, k_d = referenceFrame2.getIJK()

    R = np.array([[np.dot(i,i_d), np.dot(j,i_d), np.dot(k,i_d)],
                  [np.dot(i,j_d), np.dot(j,j_d), np.dot(k,j_d)],
                  [np.dot(i,k_d), np.dot(j,k_d), np.dot(k,k_d)]])
    return R

def euler2rotationMatrix(phi, theta, psi):
    """
    Get rotation matrix defined by phi, theta, psi.
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
    return R

def quaternion2rotationMatrix(w, x, y, z):
    """
    Get rotation matrix defined by quaternion [w, x, y, z].

    Returns:
        R (np.array): Rotation matrix equivalent of quaternion.
    """
    R = np.array([[w**2 + x**2 - y**2 - z**2, (2*x*y) - (2*w*z), (2*x*z) + (2*w*y)],
                  [(2*x*y) + (2*w*z), w**2 - x**2 + y**2 - z**2, (2*y*z) + (2*w*x)],
                  [(2*x*z) - (2*w*y), (2*y*z) + (2*w*x), w**2 - x**2 - y**2 + z**2]])
    return R

def rotationMatrix2quaternion(R):
    """
    Get quaternion defined by rotation matrix R.

    Returns:
        quaternion (np.array): quaternion equivalent of R.
    """
    w = np.sqrt((1 + R[0,0]**2 + R[1,1]**2 + R[2,2]**2) / 4)
    x = (R[2,1] - R[1,2]) / (4 * w)
    y = (R[0,2] - R[2,0]) / (4 * w)
    z = (R[1,0] - R[0,1]) / (4 * w)
    quaternion = np.array([w, x, y, z])
    return quaternion

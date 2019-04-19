# Date: 06/01/2019
# Author: Callum Bruce
# Math helper module

import numpy as np
from pyquaternion import Quaternion

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

def euler2rotationMatrix(euler):
    """
    Get rotation matrix defined by phi, theta, psi.

    Args:
        euler (list/np.array): Euler angles to convert.

    Returns:
        R (np.array): Rotation matrix representation of Euler angles.
    """
    phi = euler[0]
    theta = euler[1]
    psi = euler[2]
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

def rotationMatrix2euler(R):
    """
    Get Euler angles representation of rotation matrix R.

    Args:
        R (np.array): Rotation matrix to convert.

    Returns:
        euler (np.array): Euler angles representation of rotation matrix.
    """
    quaternion = rotationMatrix2quaternion(R)
    euler = quaternion2euler(quaternion)
    return euler

def quaternion2rotationMatrix(quaternion):
    """
    Get rotation matrix representation of quaternion [w, x, y, z].

    Args:
        quaternion (list/np.array): Quaternion to convert.

    Returns:
        R (np.array): Rotation matrix representation of quaternion.
    """
    w = quaternion[0]
    x = quaternion[1]
    y = quaternion[2]
    z = quaternion[3]
    R = np.array([[w**2 + x**2 - y**2 - z**2, (2*x*y) - (2*w*z), (2*x*z) + (2*w*y)],
                  [(2*x*y) + (2*w*z), w**2 - x**2 + y**2 - z**2, (2*y*z) + (2*w*x)],
                  [(2*x*z) - (2*w*y), (2*y*z) + (2*w*x), w**2 - x**2 - y**2 + z**2]])
    return R

def rotationMatrix2quaternion(R):
    """
    Get quaternion representation of rotation matrix R.

    Args:
        R (np.array): Rotation matrix to convert.

    Returns:
        quaternion (np.array): Quaternion representation of R.
    """
    w = np.sqrt((1 + R[0,0]**2 + R[1,1]**2 + R[2,2]**2) / 4)
    x = (R[2,1] - R[1,2]) / (4 * w)
    y = (R[0,2] - R[2,0]) / (4 * w)
    z = (R[1,0] - R[0,1]) / (4 * w)
    quaternion = np.array([w, x, y, z])
    quaternion = Quaternion(quaternion)
    return quaternion

def euler2quaternion(euler):
    """
    Get quaternion representation of Euler angles phi, theta, psi.

    Args:
        euler (list/np.array): Euler angles to convert.

    Returns:
        quaternion (np.array): Quaternion representation of Euler angles.
    """
    phi = euler[0]
    theta = euler[1]
    psi = euler[2]
    '''
    w = (np.cos(phi / 2) * np.cos(theta / 2) * np.cos(psi / 2)) + (np.sin(phi / 2) * np.sin(theta / 2) * np.sin(psi / 2))
    x = (np.sin(phi / 2) * np.cos(theta / 2) * np.cos(psi / 2)) - (np.cos(phi / 2) * np.sin(theta / 2) * np.sin(psi / 2))
    y = (np.cos(phi / 2) * np.sin(theta / 2) * np.cos(psi / 2)) + (np.sin(phi / 2) * np.cos(theta / 2) * np.sin(psi / 2))
    z = (np.cos(phi / 2) * np.cos(theta / 2) * np.sin(psi / 2)) - (np.sin(phi / 2) * np.sin(theta / 2) * np.cos(psi / 2))
    quaternion = np.array([w, x, y, z])
    '''
    q1 = Quaternion(axis=[1, 0, 0], angle=phi)
    q2 = Quaternion(axis=[0, 1, 0], angle=theta)
    q3 = Quaternion(axis=[0, 0, 1], angle=psi)
    quaternion = q3 * q2 * q1
    return quaternion

def quaternion2euler(quaternion):
    """
    Get Euler angles representation of quaternion [w, x, y, z].

    Args:
        quaternion (list/np.array): Quaternion to convert.

    Returns:
        euler (np.array): Euler angles representation of quaternion.
    """
    w = quaternion[0]
    x = quaternion[1]
    y = quaternion[2]
    z = quaternion[3]
    phi = np.arctan2(2 * ((w * x) + (y * z)), 1 - 2 * (x**2 + y**2))
    theta = np.arcsin(2 * ((w * y) - (z * x)))
    psi = np.arctan2(2 * ((w * z) + (x * y)), 1 - 2 * (y**2 + z**2))
    euler = np.array([phi, theta, psi])
    return euler

def heading2vector(heading):
    """
    Get vector representation of heading.

    Args:
        Heading (list): Heading [direction, pitch] (rad).

    Returns:
        vector (np.array): Unit vector representation of heading.
    """
    direction = heading[0]
    pitch = heading[1]
    R = euler2rotationMatrix([0, pitch, direction])
    vector = np.dot(R, [1,0,0])
    return vector

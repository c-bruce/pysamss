# Date: 06/01/2019
# Author: Callum Bruce
# ReferenceFrame Class
import numpy as np
from mayavi import mlab

class ReferenceFrame:
    """
    ReferenceFrame class.
    """
    def __init__(self, name=None):
        self.i = np.array([1, 0, 0])
        self.j = np.array([0, 1, 0])
        self.k = np.array([0, 0, 1])
        self.name = name

    def rotate(self, quaternion):
        """
        Rotate ReferenceFrame by quaternion.

        Args:
            quaternion (Quaternion): Quaternion to rotate by.
        """
        i = quaternion.rotate(self.i)
        j = quaternion.rotate(self.j)
        k = quaternion.rotate(self.k)
        self.setIJK(i, j, k)

    def rotateAbs(self, quaternion):
        """
        Rotate ReferenceFrame by quaternion. Performs absolute rotation from
        univeralRF.

        Args:
            quaternion (Quaternion): Quaternion to rotate by.
        """
        self.i = np.array([1, 0, 0])
        self.j = np.array([0, 1, 0])
        self.k = np.array([0, 0, 1])
        i = quaternion.rotate(self.i)
        j = quaternion.rotate(self.j)
        k = quaternion.rotate(self.k)
        self.setIJK(i, j, k)

    def getIJK(self):
        """ Get i, j and k vectors. """
        return self.i, self.j, self.k

    def setIJK(self, i, j, k):
        """
        Set i, j and k vectors in universalRF.

        Args:
            i (np.array): Numpy array i vector i.e. np.array([1, 0, 0])
            j (np.array): Numpy array j vector i.e. np.array([0, 1, 0])
            k (np.array): Numpy array k vector i.e. np.array([0, 0, 1])
        """
        self.i = i
        self.j = j
        self.k = k
    
    def setName(self, name):
        """
        Set reference frame name.

        Args:
            name (str): Reference frame name.
        """
        self.name = name

    def plot(self, figure, origin, scale_factor=None):
        """
        Plot reference frame centered at origin using mayavi.

        Args:
            figure (mlab.figure): Mayavi figure for plot.
            origin (list): Origin of reference frame in universalRF i.e. [x, y, z]
        """
        if scale_factor == None:
            scale_factor = 1
        mlab.quiver3d(origin[0], origin[1], origin[2], self.i[0], self.i[1], self.i[2], scale_factor=scale_factor, color=(1, 0, 0), figure=figure)
        mlab.quiver3d(origin[0], origin[1], origin[2], self.j[0], self.j[1], self.j[2], scale_factor=scale_factor, color=(0, 1, 0), figure=figure)
        mlab.quiver3d(origin[0], origin[1], origin[2], self.k[0], self.k[1], self.k[2], scale_factor=scale_factor, color=(0, 0, 1), figure=figure)

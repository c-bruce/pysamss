# Date: 06/01/2019
# Author: Callum Bruce
# CelestialBody Class
import numpy as np
import copy
from .rigidbody import RigidBody
from .referenceframe import ReferenceFrame
from ..helpermath.helpermath import *

class CelestialBody(RigidBody):
    """
    CelestialBody class.

    Args:
        mass (float): CelestialBody mass (kg).
        radius (float): CelestialBody radius (m).
        state (list): State vector [u, v, w, x, y, z, phi_d, theta_d, psi_d, w, x, y, z].
        parent (parent object): Parent object to inherit parentRF from.
    """
    def __init__(self, mass, radius, state=None, parent=None):
        self.mass = mass
        self.I = np.array([[(2 / 5) * mass * radius**2, 0, 0],
                           [0, (2 / 5) * mass * radius**2, 0],
                           [0, 0, (2 / 5) * mass * radius**2]])
        self.radius = radius
        if state == None:
            self.state = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]]
        else:
            self.state = [state]
        self.U = [[0, 0, 0, 0, 0, 0]] # [Fx, Fy, Fz, Mx, My, Mz]
        self.universalRF = ReferenceFrame()
        if parent == None: # If there is no parent the body's parentRF is the univeralRF
            self.parentRF = self.universalRF
            self.bodyRF = copy.copy(self.universalRF)
            self.parent = None
        else: # Else the body's parentRF is the parents bodyRF
            self.parentRF = parent.bodyRF
            self.bodyRF = copy.copy(parent.bodyRF)
            self.parent = parent

    def getMass(self):
        """ Get mass. """
        return self.mass

    def getI(self):
        """ Get inertia matrix I. """
        return self.I

    def getRadius(self):
        """ Get radius. """
        return self.radius

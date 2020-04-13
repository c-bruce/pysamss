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
        name (str): CelestialBody name.
        mass (float): CelestialBody mass (kg).
        radius (float): CelestialBody radius (m).
        state (np.array): State vector [u, v, w, x, y, z, phi_d, theta_d, psi_d, qw, qx, qy, qz].
        U (np.array): U vector [Fx, Fy, Fz, Mx, My, Mz].
        parent_name (str): Name of parent RigidBody object.
    """
    def __init__(self, name, mass, radius, state=None, U=None, parent_name=None):
        RigidBody.__init__(self, name, state=state, U=U, parent_name=parent_name)
        self.mass = mass
        self.radius = radius
        self.I = self.getI()

    def getMass(self):
        """ Get mass. """
        return self.mass
    
    def getRadius(self):
        """ Get radius. """
        return self.radius

    def getI(self):
        """ Get inertia matrix I. """
        I = np.array([[(2 / 5) * self.mass * self.radius**2, 0.0, 0.0],
                      [0.0, (2 / 5) * self.mass * self.radius**2, 0.0],
                      [0.0, 0.0, (2 / 5) * self.mass * self.radius**2]])
        return I

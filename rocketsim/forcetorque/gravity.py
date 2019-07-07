# Date: 06/01/2019
# Author: Callum Bruce
# Calculate force due to gravity acting on objects
import numpy as np
from ..helpermath.helpermath import *

def gravity(obj0, obj1):
    """
    Calculate gravityForce acting on an obj1 (body or vehicle).

    Args:
        obj0 (obj): CelestialBody object.
        obj1 (obj): CelestialBody or Vessel object.

    Returns:
        gravityForce (np.array): gravityForce acting on obj1.
    """
    G = 6.67408e-11 # Gravitational constant [m**3.kg**-1.s**-2]
    obj0Mass = obj0.getMass()
    obj1Mass = obj1.getMass()
    obj0Position = obj0.getPosition()
    obj1Position = obj1.getPosition()
    r = np.linalg.norm(obj0Position - obj1Position)
    F = G * ((obj0Mass * obj1Mass) / r**2)
    gravityForce = F * (obj0Position - obj1Position) / np.linalg.norm(obj0Position - obj1Position)
    return gravityForce

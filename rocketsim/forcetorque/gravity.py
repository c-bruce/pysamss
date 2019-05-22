# Date: 06/01/2019
# Author: Callum Bruce
# Calculate force due to gravity acting on objects
import numpy as np
from ..helpermath.helpermath import *

def gravity(obj1, obj2):
    """
    Calculate gravityForce acting on an obj2 (body or vehicle.

    Args:
        obj1 (obj): Body or vehicle object
        obj2 (obj): Body or vehicle object

    Returns:
        gravityForce (np.array): gravityForce acting on obj2.
    """
    G = 6.67408e-11 # Gravitational constant [m**3.kg**-1.s**-2]
    obj1Mass = obj1.getMass()
    obj2Mass = obj2.getMass()
    obj1Position = obj1.getPosition()
    obj2Position = obj2.getPosition()
    r = np.linalg.norm(obj1Position - obj2Position)
    F = G * ((obj1Mass * obj2Mass) / r**2)
    gravityForce = F * (obj1Position - obj2Position) / np.linalg.norm(obj1Position - obj2Position)
    return gravityForce

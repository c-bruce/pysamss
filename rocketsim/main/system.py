# Date: 12/06/2019
# Author: Callum Bruce
# System Class
import numpy as np
from .referenceframe import ReferenceFrame
from ..helpermath.helpermath import *

class System:
    """
    System class.

    Args:
        celestial_bodies (list): List of CelestialBody objects in system.
        vessels (list): List of Vessel objects in system.
    """
    def __init__(self, celestial_bodies, vessels):
        self.celestial_bodies = celestial_bodies
        self.vessels = vessels

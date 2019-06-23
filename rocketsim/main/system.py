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
        celestial_bodies (dict): Dict of CelestialBody objects in system.
        vessels (dict): Dict of Vessel objects in system.
    """
    def __init__(self, celestial_bodies=None, vessels=None):
        if celestial_bodies == None:
            self.celestial_bodies = {}
        else:
            self.celestial_bodies = celestial_bodies
        if vessels == None:
            self.vessels = {}
        else:
            self.vessels = vessels
        self.time = [0]
        self.endtime = 100
        self.dt = 0.1

    def set_endtime(self, endtime):
        """
        Set system end time [s].
        """
        self.endtime = endtime

    def set_dt(self, dt):
        """
        Set timestep, dt [s].
        """
        self.dt = dt

    def addCelestialBody(self, celestial_body):
        """
        Add a CelestialBody to the system.
        """
        self.celestial_bodies[celestial_body.name] = celestial_body

    def addVessel(self, vessel):
        """
        Add a Vessel to the system.
        """
        self.vessels[vessel.name] = vessel

    def save(self, path):
        """
        Save system to file
        ##### .h5 or text #####
        """

    def load(self, path):
        """
        Save system to file
        ##### .h5 or text #####
        """

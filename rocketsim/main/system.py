# Date: 12/06/2019
# Author: Callum Bruce
# System Class
import numpy as np
import itertools
import h5py
from .referenceframe import ReferenceFrame
from ..helpermath.helpermath import *
from ..simulate.simulate import simulate
from ..simulate.integrationschemes import euler
from ..forcetorque.gravity import gravity
from ..forcetorque.thrust import thrust

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
        self.scheme = euler

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

        Args:
            celestial_body (obj): CelestialBody object to add to system.
        """
        self.celestial_bodies[celestial_body.name] = celestial_body

    def addVessel(self, vessel):
        """
        Add a Vessel to the system.

        Args:
            vessel (obj): Vessel object to add to system.
        """
        self.vessels[vessel.name] = vessel

    def getCelestialBodyInteractions(self):
        """
        Get list of CelestialBody interactions.

        Returns:
            celestial_body_interactions (list): List of CelestialBody interactions.
        """
        celestial_body_interactions = list(itertools.combinations(list(self.celestial_bodies.keys()), 2))
        celestial_body_interactions = [list(celestial_body_interactions[i]) for i in range(0, len(celestial_body_interactions))]
        return celestial_body_interactions

    def getVesselsInteractions(self):
        """
        Get list of Vessel interactions.

        Returns:
            vessels_interactions (list): List of Vessel interactions.
        """
        celestial_bodies = list(self.celestial_bodies.keys())
        vessels = list(self.vessels.keys())
        vessels_interactions = []
        for vessel in vessels:
            for celestial_body in celestial_bodies:
                vessels_interactions.append([celestial_body, vessel])
        return vessels_interactions

    def setScheme(self, scheme):
        """
        Set integration scheme to use for simulating the system.
        """
        self.scheme = scheme

    def simulateSystem(self):
        """
        Simulate the system forward from current time.
        """
        celestial_body_interactions = self.getCelestialBodyInteractions()
        vessels_interactions = self.getVesselsInteractions()
        iterations = int((self.endtime - self.time[-1]) / self.dt)
        for i in range(0, iterations):
            # Step 1: Calculate forces
            # Celestial Bodies:
            ## Gravity
            for interaction in celestial_body_interactions:
                obj0 = self.celestial_bodies[interaction[0]]
                obj1 = self.celestial_bodies[interaction[1]]
                gravityForce = gravity(obj0, obj1)
                obj0.addForce(-gravityForce)
                obj1.addForce(gravityForce)
            # Vessels:
            ## Gravity
            for interaction in vessels_interactions:
                obj0 = self.celestial_bodies[interaction[0]]
                obj1 = self.vessels[interaction[1]]
                gravityForce = gravity(obj0, obj1)
                obj1.addForce(gravityForce)
            # Step 2: Simulate timestep
            # Celestial Bodies:
            for celestial_body in self.celestial_bodies:
                simulate(self.celestial_bodies[celestial_body], self.scheme, self.dt)
            # Vessels:
            for vessel in self.vessels:
                simulate(self.vessels[vessel], self.scheme, self.dt)
            # Step 3: Iterate on time
            self.time.append(self.time[-1] + self.dt)

    def save(self, path):
        """
        Save system to .h5 file.
        """
        f = h5py.File(path + '.h5', 'a')
        # Celestial Bodies
        f.create_group('celestial_bodies')
        for celestial_body in self.celestial_bodies:
            obj = self.celestial_bodies[celestial_body]
            group = f.create_group('celestial_bodies/' + obj.name)
            '''
            group.attrs.create('name', obj.name, dtype=np.dtype('U')
            group.attrs.create('mass', obj.mass)
            group.attrs.create('I', obj.I)
            group.attrs.create('radius', obj.radius)
            group.attrs.create('parent', obj.parent.name)
            group.attrs.create('bodyRF_i', obj.bodyRF.i)
            group.attrs.create('bodyRF_j', obj.bodyRF.j)
            group.attrs.create('bodyRF_k', obj.bodyRF.k)
            '''
            group.create_dataset('state', data=np.array(obj.state))
            group.create_dataset('U', data=np.array(obj.U))
        f.close()

    def load(self, path):
        """
        Save system to file
        ##### .h5 or text #####
        """

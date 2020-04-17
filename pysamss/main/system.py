# Date: 12/06/2019
# Author: Callum Bruce
# System Class
import numpy as np
import copy
import itertools
import h5py
import glob
import os
from .timestep import Timestep
from .referenceframe import ReferenceFrame
from .celestialbody import CelestialBody
from .vessel import Vessel
from .stage import Stage
from ..helpermath.helpermath import *
from ..simulate.simulate import simulate
from ..simulate.integrationschemes import euler
from ..forcetorque.gravity import gravity
from ..forcetorque.thrust import thrust

class System:
    """
    System class.

    Args:
        name (str): System name. Used to create *_data folder.
        timesteps (dict): Dict of system timesteps.
        celestial_bodies (dict): Dict of CelestialBody objects in system.
        vessels (dict): Dict of Vessel objects in system.
    """
    def __init__(self, name):
        self.name = name
        self.save_directory = self.name + '_data'
        self.currenttimestep = Timestep(0.0)
        self.timesteps = {}
        self.dt = 0.1
        self.endtime = 100.0
        self.saveinterval = 1
        self.scheme = euler

    def save(self, path=None):
        """
        Save system.
        """
        # Create save file if it does not already exist
        if not(os.path.exists(self.name + '.psm')):
            open(self.name + '.psm', 'a').close()
        # Create save directory if it does not already exist
        if not(os.path.exists(self.save_directory)):
            os.mkdir(self.save_directory)
        if path is None:
            path = self.save_directory + '/' + str(self.currenttimestep.time) + '.h5'
        f = h5py.File(path, 'a')
        # System class
        f.attrs.create('name', np.string_(self.name))
        f.attrs.create('save_directory', np.string_(self.save_directory))
        f.attrs.create('dt', self.dt)
        f.attrs.create('endtime', self.endtime)
        f.attrs.create('saveinterval', int(self.saveinterval))
        self.currenttimestep.save(f)
        f.close()

    def load(self, path):
        """
        Load system.

        Args:
            path (str): Path to *.psm file.
        """
        timestep_paths = glob.glob(path[:-4] + '_data/*.h5')
        timesteps = []
        for timestep_path in timestep_paths:
            timesteps.append(float(timestep_path[(len(path) + 2):-3]))
        timesteps, timestep_paths = (list(t) for t in zip(*sorted(zip(timesteps, timestep_paths))))
        timesteps = dict(zip(timesteps, timestep_paths))
        path = list(timesteps.values())[-1]
        f = h5py.File(path, 'r')
        self.currenttimestep.load(f) # Load last save timestep
        f.close()
    
    def getName(self):
        """
        Get system name.

        Returns:
            name (str): System name.
        """
        return self.name

    def setName(self, name):
        """
        Set system name.

        Args:
            name (str): System name.
        """
        self.name = name
    
    def getEndTime(self):
        """
        Get system endtime.

        Returns:
            endtime (str): System endtime.
        """
        return self.endtime

    def setEndTime(self, endtime):
        """
        Set system end time [s].

        Args:
            endtime (str): System endtime.
        """
        self.endtime = endtime

    def getDt(self):
        """
        Get timestep, dt [s].

        Returns:
            dt (float): System dt.
        """
        return self.dt
    
    def setDt(self, dt):
        """
        Set timestep, dt [s].

        Args:
            dt (float): System dt.
        """
        self.dt = dt
    
    def getSaveInterval(self):
        """
        Get save interval - every nth timestep.

        Returns:
            saveinterval (float): System saveinterval.
        """
        return self.saveinterval
    
    def setSaveInterval(self, saveinterval):
        """
        Set save interval - every nth timestep.

        Args:
            saveinterval (float): System saveinterval.
        """
        self.saveinterval = saveinterval
    
    def setScheme(self, scheme):
        """
        Set integration scheme to use for simulating the system.
        """
        self.scheme = scheme

    def getCelestialBodyInteractions(self):
        """
        Get list of CelestialBody interactions.

        Returns:
            celestial_body_interactions (list): List of CelestialBody interactions.
        """
        celestial_body_interactions = list(itertools.combinations(list(self.currenttimestep.celestial_bodies.keys()), 2))
        celestial_body_interactions = [list(celestial_body_interactions[i]) for i in range(0, len(celestial_body_interactions))]
        return celestial_body_interactions

    def getVesselsInteractions(self):
        """
        Get list of Vessel interactions.

        Returns:
            vessels_interactions (list): List of Vessel interactions.
        """
        celestial_bodies = list(self.currenttimestep.celestial_bodies.keys())
        vessels = list(self.currenttimestep.vessels.keys())
        vessels_interactions = []
        for vessel in vessels:
            for celestial_body in celestial_bodies:
                vessels_interactions.append([celestial_body, vessel])
        return vessels_interactions

    def simulateSystem(self):
        """
        Simulate the system forward from current time.
        """
        celestial_body_interactions = self.getCelestialBodyInteractions()
        vessels_interactions = self.getVesselsInteractions()
        iterations = int((self.endtime - self.currenttimestep.time) / self.dt)
        for i in range(0, iterations):
            # Step 1: Calculate forces
            # Celestial Bodies:
            ## Gravity
            for interaction in celestial_body_interactions:
                obj0 = self.currenttimestep.celestial_bodies[interaction[0]]
                obj1 = self.currenttimestep.celestial_bodies[interaction[1]]
                gravityForce = gravity(obj0, obj1)
                obj0.addForce(-gravityForce)
                obj1.addForce(gravityForce)
            # Vessels:
            ## Gravity
            for interaction in vessels_interactions:
                obj0 = self.currenttimestep.celestial_bodies[interaction[0]]
                obj1 = self.currenttimestep.vessels[interaction[1]]
                gravityForce = gravity(obj0, obj1)
                obj1.addForce(gravityForce)
            # Step 2: Save data - included at this stage so that U is populated
            if i % self.saveinterval == 0:
                self.save()
            # Step 3: Simulate timestep
            # Celestial Bodies:
            for celestial_body in self.currenttimestep.celestial_bodies:
                simulate(self.currenttimestep.celestial_bodies[celestial_body], self.scheme, self.dt)
            # Vessels:
            for vessel in self.currenttimestep.vessels:
                simulate(self.currenttimestep.vessels[vessel], self.scheme, self.dt)
            # Step 4: Iterate on time
            self.currenttimestep.setTime(self.currenttimestep.time + self.dt)
            progress = (i / iterations) * 100
            print("Progress: " + str(np.around(progress, decimals = 2)) + " %.", end="\r")
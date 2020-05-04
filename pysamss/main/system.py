# Date: 12/06/2019
# Author: Callum Bruce
# System Class
import numpy as np
import copy
import itertools
import h5py
import glob
import os
from tvtk.api import tvtk # python wrappers for the C++ vtk ecosystem
import shutil
import datetime
import julian
from .timestep import Timestep
from .referenceframe import ReferenceFrame
from .celestialbody import CelestialBody
from .vessel import Vessel
from .stage import Stage
from ..helpermath.helpermath import *
from ..forcetorque.gravity import gravity
from ..forcetorque.thrust import thrust

class System:
    """
    System class.

    Args:
        name (str): System name. Used to create *_data folder.
    """
    def __init__(self, name):
        self.name = name
        self.save_directory = self.name + '_data'
        self.current = Timestep()
        self.timesteps = {0 : self.current}
        self.dt = 0.1
        self.endtime = 100.0
        self.saveinterval = 1
        self.scheme = 'euler'

    def save(self):
        """
        Save system.
        """
        # Create save file if it does not already exist
        if not(os.path.exists(self.name + '.psm')):
            open(self.name + '.psm', 'a').close()
        # Create save directory if it does not already exist
        if not(os.path.exists(self.save_directory)):
            os.mkdir(self.save_directory)
        path = self.save_directory + '/' + str(int(self.current.savefile)) + '.h5'
        f = h5py.File(path, 'a')
        # System class
        f.attrs.create('name', np.string_(self.name))
        f.attrs.create('save_directory', np.string_(self.save_directory))
        f.attrs.create('dt', self.dt)
        f.attrs.create('endtime', self.endtime)
        f.attrs.create('saveinterval', int(self.saveinterval))
        self.current.save(f)
        f.close()
    
    def load(self, path, getAll=True):
        """
        Load system data.

        Args:
            path (str): Path to *.psm file.
            getAll (bool): Load all data boolean. Default = True.
        """
        # Reset timesteps dict
        self.setName(path[:-4])
        self.save_directory = self.name + '_data'
        self.timesteps = {}
        # Load data into timesteps dict
        timestep_paths = glob.glob(self.save_directory + '/*.h5')
        if getAll:
            i = 0
            for timestep_path in timestep_paths:
                f = h5py.File(timestep_path, 'r')
                new_timestep = Timestep()
                new_timestep.load(f)
                if i == len(timestep_paths):
                    self.setDt(f.attrs['dt'])
                    self.setEndTime(f.attrs['endtime'])
                    self.setSaveInterval(f.attrs['saveinterval'])
                f.close()
                self.timesteps[new_timestep.savefile] = new_timestep
                i += 1
                progress = (i / len(timestep_paths)) * 100
                print("Load; Progress: " + str(np.around(progress, decimals = 2)) + " %.", end="\r")
            print('\n')
        else:
            timestep_path = timestep_paths[-1]
            f = h5py.File(timestep_path, 'r')
            new_timestep = Timestep()
            new_timestep.load(f)
            self.setDt(f.attrs['dt'])
            self.setEndTime(f.attrs['endtime'])
            self.setSaveInterval(f.attrs['saveinterval'])
            f.close()
            self.timesteps[new_timestep.time] = new_timestep
        # Set current timestep to the last one in timesteps dict
        self.setCurrent(self.timesteps[max(list(self.timesteps.keys()))])
    
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
    
    def getCurrent(self):
        """
        Get the System current Timestep.

        Returns:
            current (obj): System current Timestep.
        """
        return self.current
    
    def setCurrent(self, timestep):
        """
        Set the System current Timestep.

        Args:
            timestep (obj): Timestep to set System current timestep to.
        """
        self.current = timestep
    
    def addTimestep(self, timestep):
        """
        Add a Timestep to the system.

        Args:
            timestep (obj): Timestep object to add to system.
        """
        self.timesteps[timestep.time] = timestep
    
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
        Get saveinterval - every nth timestep.

        Returns:
            saveinterval (float): System saveinterval.
        """
        return self.saveinterval
    
    def setSaveInterval(self, saveinterval):
        """
        Set saveinterval - every nth timestep.

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
        celestial_body_interactions = list(itertools.combinations(list(self.current.celestial_bodies.keys()), 2))
        celestial_body_interactions = [list(celestial_body_interactions[i]) for i in range(0, len(celestial_body_interactions))]
        return celestial_body_interactions

    def getVesselsInteractions(self):
        """
        Get list of Vessel interactions.

        Returns:
            vessels_interactions (list): List of Vessel interactions.
        """
        celestial_bodies = list(self.current.celestial_bodies.keys())
        vessels = list(self.current.vessels.keys())
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
        iterations = int((self.endtime - self.current.time) / self.dt)
        for i in range(0, iterations):
            # Step 1: Calculate forces
            # Celestial Bodies:
            ## Gravity
            for interaction in celestial_body_interactions:
                obj0 = self.current.celestial_bodies[interaction[0]]
                obj1 = self.current.celestial_bodies[interaction[1]]
                gravityForce = gravity(obj0, obj1)
                obj0.addForce(-gravityForce)
                obj1.addForce(gravityForce)
            # Vessels:
            ## Gravity
            for interaction in vessels_interactions:
                obj0 = self.current.celestial_bodies[interaction[0]]
                obj1 = self.current.vessels[interaction[1]]
                gravityForce = gravity(obj0, obj1)
                obj1.addForce(gravityForce)
            # Step 2: Save data - included at this stage so that U is populated
            if i % self.saveinterval == 0:
                self.current.setSaveFile(int(i / self.saveinterval))
                self.save()
            # Step 3: Simulate timestep
            # Celestial Bodies:
            for celestial_body in self.current.celestial_bodies.values():
                celestial_body.simulate(self.dt, celestial_body.euler)
            # Vessels:
            for vessel in self.current.vessels.values():
                vessel.simulate(self.dt, vessel.euler)
            # Step 4: Iterate on time
            self.current.setTime(self.current.time + self.dt)
            self.current.setDatetime(self.current.date_time + datetime.timedelta(0, self.dt))
            progress = (i / iterations) * 100
            print("Simulate System; Progress: " + str(np.around(progress, decimals = 2)) + " %.", end="\r")
        print('\n')
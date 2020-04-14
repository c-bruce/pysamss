# Date: 12/06/2019
# Author: Callum Bruce
# System Class
import numpy as np
import copy
import itertools
import h5py
import glob
import os
from .celestialbody import CelestialBody
from .vessel import Vessel
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
        name (str): System name. Used to create *_data folder.
        timesteps (dict): Dict of system timesteps.
        celestial_bodies (dict): Dict of CelestialBody objects in system.
        vessels (dict): Dict of Vessel objects in system.
    """
    def __init__(self, name=None, timesteps=None, celestial_bodies=None, vessels=None):
        self.name = name
        if name != None:
            self.save_directory = self.name + '_data'
        self.systemRF = ReferenceFrame()
        if timesteps == None:
            self.timesteps = {}
        else:
            self.timesteps = timesteps
        if celestial_bodies == None:
            self.celestial_bodies = {}
        else:
            self.celestial_bodies = celestial_bodies
        if vessels == None:
            self.vessels = {}
        else:
            self.vessels = vessels
        self.time = 0.0
        self.endtime = 100.0
        self.dt = 0.1
        self.saveinterval = 1
        self.scheme = euler
    
    def set_time(self, time):
        """
        Set system current time [s].
        """
        self.time = time

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
    
    def set_saveinterval(self, saveinterval):
        """
        Set save interval - every nth timestep.
        """
        self.saveinterval = saveinterval

    def addCelestialBody(self, celestial_body):
        """
        Add a CelestialBody to the system.

        Args:
            celestial_body (obj): CelestialBody object to add to system.
        """
        if celestial_body.parent_name is None: # If there is no parent the body's parentRF is the systemRF
            celestial_body.setParent(None)
            celestial_body.setUniversalRF(self.systemRF)
            celestial_body.setParentRF(self.systemRF)
            celestial_body.setBodyRF(copy.copy(self.systemRF))
            self.celestial_bodies[celestial_body.name] = celestial_body
        else: # Else the body's parentRF is the parents bodyRF
            if celestial_body.parent_name in self.celestial_bodies:
                celestial_body.setParent(self.celestial_bodies[celestial_body.parent_name])
                celestial_body.setUniversalRF(self.systemRF)
                celestial_body.setParentRF(celestial_body.parent.bodyRF)
                celestial_body.setBodyRF(copy.copy(celestial_body.parent.bodyRF))
                self.celestial_bodies[celestial_body.name] = celestial_body
            else:
                print('Error: Parent "' + celestial_body.parent_name + '" does not exist. Unable to add "' + celestial_body.name + '" to System.')
        
    def addVessel(self, vessel):
        """
        Add a Vessel to the system.

        Args:
            vessel (obj): Vessel object to add to system.
        """
        #self.vessels[vessel.name] = vessel
        if vessel.parent_name is None: # If there is no parent the body's parentRF is the systemRF
            vessel.setParent(None)
            vessel.setUniversalRF(self.systemRF)
            vessel.setParentRF(self.systemRF)
            vessel.setBodyRF(copy.copy(self.systemRF))
            vessel.initPosition()
            self.vessels[vessel.name] = vessel
        else: # Else the body's parentRF is the parents bodyRF
            if vessel.parent_name in self.celestial_bodies:
                vessel.setParent(self.celestial_bodies[vessel.parent_name])
                vessel.setUniversalRF(self.systemRF)
                vessel.setParentRF(vessel.parent.bodyRF)
                vessel.setBodyRF(copy.copy(vessel.parent.bodyRF))
                vessel.initPosition()
                self.vessels[vessel.name] = vessel
            else:
                print('Error: Parent "' + vessel.parent_name + '" does not exist. Unable to add "' + vessel.name + '" to System.')

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
        iterations = int((self.endtime - self.time) / self.dt)
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
            # Step 2: Save data - included at this stage so that U is populated
            if i % self.saveinterval == 0:
                self.saveTimestep(self.save_directory + '/' + str(self.time))
                self.timesteps.update({self.time : self.save_directory + '/' + str(self.time) + '.h5'})
            # Step 3: Simulate timestep
            # Celestial Bodies:
            for celestial_body in self.celestial_bodies:
                simulate(self.celestial_bodies[celestial_body], self.scheme, self.dt)
            # Vessels:
            for vessel in self.vessels:
                simulate(self.vessels[vessel], self.scheme, self.dt)
            # Step 4: Iterate on time
            self.set_time(self.time + self.dt)
            progress = (i / iterations) * 100
            print("Progress: " + str(np.around(progress, decimals = 2)) + " %.", end="\r")

    def saveTimestep(self, path):
        """
        Save timestep to .h5 file.
        """
        f = h5py.File(path + '.h5', 'a')
        # Celestial Bodies
        f.create_group('celestial_bodies')
        for celestial_body in self.celestial_bodies:
            obj = self.celestial_bodies[celestial_body]
            group = f.create_group('celestial_bodies/' + obj.name)
            # Save attributes - alphabetical order
            group.attrs.create('mass', obj.mass)
            group.attrs.create('name', np.string_(obj.name))
            try:
                group.attrs.create('parent_name', np.string_(obj.parent.name))
            except AttributeError:
                group.attrs.create('parent_name', np.string_('None'))
            group.attrs.create('radius', obj.radius)
            # Save datasets - alphabetical order
            group.create_dataset('bodyRF_i', data=obj.bodyRF.i)
            group.create_dataset('bodyRF_j', data=obj.bodyRF.j)
            group.create_dataset('bodyRF_k', data=obj.bodyRF.k)
            group.create_dataset('I', data=obj.I)
            group.create_dataset('state', data=obj.state)
            group.create_dataset('U', data=obj.U)
        f.close()
    
    def loadTimestep(self, path):
        """
        Load timestep from .h5 file.
        """
        f = h5py.File(path, 'a')
        celestial_bodies = {} # Dictionary containing {new_celestial_body : parent (str)} for supporting setting of parents
        for celestial_body in f['celestial_bodies']:
            # Load attributes - alphabetical order
            mass = f['celestial_bodies/' + celestial_body].attrs['mass']
            name = f['celestial_bodies/' + celestial_body].attrs['name']
            parent_name = f['celestial_bodies/' + celestial_body].attrs['parent_name']
            if parent_name == 'None':
                parent_name = None
            radius = f['celestial_bodies/' + celestial_body].attrs['radius']
            # Load datasets - alphabetical order
            bodyRF_i = np.array(f['celestial_bodies/' + celestial_body].get('bodyRF_i'))
            bodyRF_j = np.array(f['celestial_bodies/' + celestial_body].get('bodyRF_j'))
            bodyRF_k = np.array(f['celestial_bodies/' + celestial_body].get('bodyRF_k'))
            #I = np.array(f['celestial_bodies/' + celestial_body].get('I'))
            state = np.array(f['celestial_bodies/' + celestial_body].get('state'))
            #U = np.array(f['celestial_bodies/' + celestial_body].get('U'))
            # Create celestial body and add it to system
            new_celestial_body = CelestialBody(name, mass, radius, state=state)
            new_celestial_body.bodyRF.setIJK(bodyRF_i, bodyRF_j, bodyRF_k)
            celestial_bodies.update({new_celestial_body : parent_name})
        # Loop through and add celestial bodies setting parents if they exist
        for celestial_body in celestial_bodies:
            parent_name = celestial_bodies[celestial_body]
            if parent_name != None:
                for parent in celestial_bodies:
                    if parent.name == parent_name:
                        celestial_body.setParent(parent)
            self.addCelestialBody(celestial_body)

        #set_time
    
    def save(self):
        """
        Save system.
        """
        open(self.name + '.psm', 'a').close() # Save a pointer file system.name.psm
        os.mkdir(self.save_directory)

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
        self.timesteps = dict(zip(timesteps, timestep_paths))
        self.loadTimestep(list(self.timesteps.values())[-1]) # Load last save timestep

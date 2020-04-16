# Date: 12/06/2019
# Author: Callum Bruce
# System Class
import numpy as np
import copy
import itertools
import h5py
import glob
import os
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
    def __init__(self, name, timesteps=None, celestial_bodies=None, vessels=None):
        self.name = name
        self.save_directory = self.name + '_data'
        self.systemRF = ReferenceFrame(name='SystemRF')
        self.time = 0.0
        self.endtime = 100.0
        self.dt = 0.1
        self.saveinterval = 1
        self.scheme = euler
        # timesteps dict
        if timesteps is None:
            self.timesteps = {}
        else:
            self.timesteps = timesteps
        # reference_frames dict
        self.reference_frames = {self.systemRF.name : self.systemRF}
        # celestial_bodies dict
        if celestial_bodies is None:
            self.celestial_bodies = {}
        else:
            self.celestial_bodies = celestial_bodies
        # vessels dict
        if vessels == None:
            self.vessels = {}
        else:
            self.vessels = vessels
    
    def set_name(self, name):
        """
        Set system name.
        """
        self.name = name
    
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
    
    def addReferenceFrame(self, reference_frame):
        """
        Add a ReferenceFrame to the system.

        Args:
            reference_frame (obj): ReferenceFrame object to add to system.
        """
        self.reference_frames[reference_frame.name] = reference_frame

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
            celestial_body.bodyRF.setName(celestial_body.name + 'RF')
            self.addReferenceFrame(celestial_body.bodyRF)
            self.celestial_bodies[celestial_body.name] = celestial_body
        else: # Else the body's parentRF is the parents bodyRF
            if celestial_body.parent_name in self.celestial_bodies:
                celestial_body.setParent(self.celestial_bodies[celestial_body.parent_name])
                celestial_body.setUniversalRF(self.systemRF)
                celestial_body.setParentRF(celestial_body.parent.bodyRF)
                celestial_body.setBodyRF(copy.copy(celestial_body.parent.bodyRF))
                celestial_body.bodyRF.setName(celestial_body.name + 'RF')
                self.addReferenceFrame(celestial_body.bodyRF)
                self.celestial_bodies[celestial_body.name] = celestial_body
            else:
                print('Error: Parent "' + celestial_body.parent_name + '" does not exist. Unable to add "' + celestial_body.name + '" to System.')
        
    def addVessel(self, vessel):
        """
        Add a Vessel to the system.

        Args:
            vessel (obj): Vessel object to add to system.
        """
        if vessel.parent_name is None: # If there is no parent the body's parentRF is the systemRF
            vessel.setParent(None)
            vessel.setUniversalRF(self.systemRF)
            vessel.setParentRF(self.systemRF)
            vessel.setBodyRF(copy.copy(self.systemRF))
            vessel.bodyRF.setName(vessel.name + 'RF')
            self.addReferenceFrame(vessel.bodyRF)
            vessel.initPosition()
            self.vessels[vessel.name] = vessel
        else: # Else the body's parentRF is the parents bodyRF
            if vessel.parent_name in self.celestial_bodies:
                vessel.setParent(self.celestial_bodies[vessel.parent_name])
                vessel.setUniversalRF(self.systemRF)
                vessel.setParentRF(vessel.parent.bodyRF)
                vessel.setBodyRF(copy.copy(vessel.parent.bodyRF))
                vessel.bodyRF.setName(vessel.name + 'RF')
                self.addReferenceFrame(vessel.bodyRF)
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
                self.__saveTimestep(self.save_directory + '/' + str(self.time) + '.h5')
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
    
    def __saveReferenceFrame(self, group, reference_frame):
        """
        Save ReferenceFrame object to .h5 file.

            Args:
                group (h5py group): HDF5 file group to save ReferenceFrame object to.
                reference_frame (obj): ReferenceFrame object to save.
        """
        group.attrs.create('name', np.string_(reference_frame.name))
        group.create_dataset('i', data=reference_frame.i)
        group.create_dataset('j', data=reference_frame.j)
        group.create_dataset('k', data=reference_frame.k)
    
    def __loadReferenceFrame(self, group):
        """
        Load ReferenceFrame object from .h5 file.

            Args:
                group (h5py group): HDF5 file group to load ReferenceFrame object from.
            
            Returns:
                reference_frame (obj): ReferenceFrame object.
        """
        # Get data
        name = group.attrs['name'].decode('UTF-8')
        i = np.array(group.get('i'))
        j = np.array(group.get('j'))
        k = np.array(group.get('k'))
        # Create ReferenceFrame object
        reference_frame = ReferenceFrame()
        reference_frame.setName(name)
        reference_frame.setIJK(i, j, k)
        return reference_frame        
    
    def __saveCelestialBody(self, group, celestial_body):
        """
        Save CelestialBody object to .h5 file.

            Args:
                group (h5py group): HDF5 file group to save CelestialBody object to.
                celestial_body (obj): CelestialBody object to save.
        """
        # Save attributes - alphabetical order
        group.attrs.create('mass', celestial_body.mass)
        group.attrs.create('name', np.string_(celestial_body.name))
        try:
            group.attrs.create('parent_name', np.string_(celestial_body.parent.name))
        except AttributeError:
            group.attrs.create('parent_name', np.string_('None'))
        group.attrs.create('radius', celestial_body.radius)
        # Save datasets - alphabetical order
        group.create_dataset('I', data=celestial_body.I)
        group.create_dataset('state', data=celestial_body.state)
        group.create_dataset('U', data=celestial_body.U)
    
    def __loadCelestialBody(self, group):
        """
        Load CelestialBody object from .h5 file.

            Args:
                group (h5py group): HDF5 file group to load CelestialBody object from.
            
            Return:
                celestial_body (obj): CelestialBody object.
        """
        # Get data
        mass = group.attrs['mass']
        name = group.attrs['name'].decode('UTF-8')
        parent_name = group.attrs['parent_name'].decode('UTF-8')
        if parent_name == 'None':
            parent_name = None
        radius = group.attrs['radius']
        I = np.array(group.get('I'))
        state = np.array(group.get('state'))
        U = np.array(group.get('U'))
        # Create CelestialBody object
        celestial_body = CelestialBody(name, mass, radius, state=state, U=U, parent_name=parent_name)
        return celestial_body
    
    def __saveVessel(self, group, vessel):
        """
        Save Vessel object to .h5 file.

            Args:
                group (h5py group): HDF5 file group to save Vessel object to.
                vessel (obj): Vessel object to save.
        """
        # Save attributes - alphabetical order
        group.attrs.create('length', vessel.length)
        group.attrs.create('mass', vessel.mass)
        group.attrs.create('name', np.string_(vessel.name))
        try:
            group.attrs.create('parent_name', np.string_(vessel.parent.name))
        except AttributeError:
            group.attrs.create('parent_name', np.string_('None'))
        # Save datasets - alphabetical order
        group.create_dataset('CoM', data=vessel.CoM)
        group.create_dataset('CoT', data=vessel.CoT)
        group.create_dataset('I', data=vessel.I)
        group.create_dataset('state', data=vessel.state)
        group.create_dataset('U', data=vessel.U)
        # Save vessel stages
        group.create_group('stages')
        i = 0
        for stage in vessel.stages:
            stage_group = group.create_group('stages/' + str(i))
            self.__saveStage(stage_group, stage)
    
    def __loadVessel(self, group):
        """
        Load Vessel object from .h5 file.

            Args:
                group (h5py group): HDF5 file group to load Vessel object from.
            
            Returns:
                vessel (obj): Vessel object.
        """
        # Get data
        name = group.attrs['name'].decode('UTF-8')
        parent_name = group.attrs['parent_name'].decode('UTF-8')
        if parent_name == 'None':
            parent_name = None
        state = np.array(group.get('state'))
        U = np.array(group.get('U'))
        stages = []
        for stage in group['stages']:
            stages.append(self.__loadStage(group['stages'][stage]))
        # Create Vessel object
        vessel = Vessel(name, stages, state=state, U=U, parent_name=parent_name)
        return vessel
    
    def __saveStage(self, group, stage):
        """
        Save Stage object to .h5 file.

            Args:
                group (h5py group): HDF5 file group to save Stage object to.
                stage (obj): Stage object to save.
        """
        # Save attributes - alphabetical order
        group.attrs.create('drymass', stage.drymass)
        group.attrs.create('length', stage.length)
        group.attrs.create('mass', stage.mass)
        group.attrs.create('radius', stage.radius)
        group.attrs.create('wetmass', stage.wetmass)
        # Save datasets - alphabetical order
        group.create_dataset('gimbal', data=stage.gimbal)
        group.create_dataset('position', data=stage.position)
    
    def __loadStage(self, group):
        """
        Load Stage object from .h5 file.

            Args:
                group (h5py group): HDF5 file group to save Stage object from.
        
            Returns:
                stage (obj): Stage object.
        """
        mass = group.attrs['mass']
        radius = group.attrs['radius']
        length = group.attrs['length']
        position = np.array(group.get('position'))
        stage = Stage(mass, radius, length, position)
        return stage

    def __saveTimestep(self, path):
        """
        Save timestep to .h5 file.
        """
        f = h5py.File(path, 'a')
        # System class
        f.attrs.create('name', np.string_(self.name))
        f.attrs.create('time', self.time)
        f.attrs.create('endtime', self.endtime)
        f.attrs.create('dt', self.dt)
        f.attrs.create('saveinterval', int(self.saveinterval))
        # ReferenceFrame class
        f.create_group('reference_frames')
        for reference_frame in self.reference_frames:
            group = f.create_group('reference_frames/' + self.reference_frames[reference_frame].name)
            self.__saveReferenceFrame(group, self.reference_frames[reference_frame])
        # CelestialBody class
        f.create_group('celestial_bodies')
        for celestial_body in self.celestial_bodies:
            group = f.create_group('celestial_bodies/' + self.celestial_bodies[celestial_body].name)
            self.__saveCelestialBody(group, self.celestial_bodies[celestial_body])
        # Vessel class
        f.create_group('vessels')
        for vessel in self.vessels:
            group = f.create_group('vessels/' + self.vessels[vessel].name)
            self.__saveVessel(group, self.vessels[vessel])
        f.close()
    
    def __loadTimestep(self, path):
        """
        Load timestep from .h5 file.
        """
        f = h5py.File(path, 'r')
        # System class
        self.set_name(f.attrs['name'].decode('UTF-8'))
        self.set_time(f.attrs['time'])
        self.set_endtime(f.attrs['endtime'])
        self.set_dt(f.attrs['dt'])
        self.set_saveinterval(f.attrs['saveinterval'])
        # ReferenceFrame class
        for reference_frame in f['reference_frames']:
            group = f['reference_frames'][reference_frame]
            new_reference_frame = self.__loadReferenceFrame(group)
            self.reference_frames[new_reference_frame.name] = new_reference_frame
        # CelestialBody class
        for celestial_body in f['celestial_bodies']:
            group = f['celestial_bodies'][celestial_body]
            new_celestial_body = self.__loadCelestialBody(group)
            self.celestial_bodies[new_celestial_body.name] = new_celestial_body
        # Vessel class
        for vessel in f['vessels']:
            group = f['vessels'][vessel]
            new_vessel = self.__loadVessel(group)
            self.vessels[new_vessel.name] = new_vessel
        # Setup universalRF, parentRF and bodyRF relationships
        # Setup parent relationships
    
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
        # Reset timesteps, reference_frames, celestial_bodies and vessels dicts
        self.timesteps = {}
        self.systemRF = ReferenceFrame(name='SystemRF')
        self.reference_frames = {self.systemRF.name : self.systemRF}
        self.celestial_bodies = {}
        self.vessels = {}
        timestep_paths = glob.glob(path[:-4] + '_data/*.h5')
        timesteps = []
        for timestep_path in timestep_paths:
            timesteps.append(float(timestep_path[(len(path) + 2):-3]))
        timesteps, timestep_paths = (list(t) for t in zip(*sorted(zip(timesteps, timestep_paths))))
        self.timesteps = dict(zip(timesteps, timestep_paths))
        self.__loadTimestep(list(self.timesteps.values())[-1]) # Load last save timestep

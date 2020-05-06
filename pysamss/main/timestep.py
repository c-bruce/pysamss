# Date: 17/04/2020
# Author: Callum Bruce
# Timestep Class
import numpy as np
import copy
import itertools
import h5py
import glob
import os
import julian
import datetime
from .referenceframe import ReferenceFrame
from .celestialbody import CelestialBody
from .vessel import Vessel
from .stage import Stage

class Timestep:
    """
    Timestep class.

    Args:
        time (float): Simulation time [s]. Default time = 0.0.
        datetime (obj): Datetime object. Default datetime = 2020-03-20 03:50:00 (2020 vernal equinox).
    """
    def __init__(self, time=None, date_time=None):
        if time is None:
            self.time = 0.0
        else:
            self.time = time
        if date_time is None:
            self.date_time = datetime.datetime(2020, 3, 20, 3, 50)
        else:
            self.date_time = date_time
        self.savefile = None
        self.universalRF = ReferenceFrame(name='UniversalRF')
        self.reference_frames = {self.universalRF.name : self.universalRF}
        self.celestial_bodies = {}
        self.vessels = {}
    
    def save(self, f):
        """
        Save timestep to .h5 file.

        Args:
            f (hdf5 file): HDF5 file to save to.
        """
        f.attrs.create('time', self.time)
        f.attrs.create('juliandate', self.getJulianDate())
        f.attrs.create('savefile', self.savefile)
        # ReferenceFrame class
        f.create_group('reference_frames')
        for reference_frame in self.reference_frames:
            group = f.create_group('reference_frames/' + self.reference_frames[reference_frame].name)
            self.reference_frames[reference_frame].save(group)
        # CelestialBody class
        f.create_group('celestial_bodies')
        for celestial_body in self.celestial_bodies:
            group = f.create_group('celestial_bodies/' + self.celestial_bodies[celestial_body].name)
            self.celestial_bodies[celestial_body].save(group)
        # Vessel class
        f.create_group('vessels')
        for vessel in self.vessels:
            group = f.create_group('vessels/' + self.vessels[vessel].name)
            self.vessels[vessel].save(group)
    
    def load(self, f):
        """
        Load timestep from .h5 file.

        Args:
            f (hdf5 file): HDF5 file to load from.
        """
        # Reset reference_frames, celestial_bodies and vessels dicts
        self.reference_frames = {}
        self.celestial_bodies = {}
        self.vessels = {}
        # Get/set data
        self.setTime(f.attrs['time'])
        self.setDatetime(julian.from_jd(f.attrs['juliandate']))
        self.setSaveFile(f.attrs['savefile'])
        # ReferenceFrame class
        for reference_frame in f['reference_frames']:
            group = f['reference_frames'][reference_frame]
            new_reference_frame = ReferenceFrame()
            new_reference_frame.load(group)
            self.reference_frames[new_reference_frame.name] = new_reference_frame
        # CelestialBody class
        for celestial_body in f['celestial_bodies']:
            group = f['celestial_bodies'][celestial_body]
            new_celestial_body = CelestialBody()
            new_celestial_body.load(group)
            self.celestial_bodies[new_celestial_body.name] = new_celestial_body
        # Vessel class
        for vessel in f['vessels']:
            group = f['vessels'][vessel]
            new_vessel = Vessel()
            new_vessel.load(group)
            self.vessels[new_vessel.name] = new_vessel
        # Setup parent and universalRF, parentRF, bodyRF relationships
        self.setRelationships()
    
    def getTime(self):
        """
        Get time [s].

        Returns:
            time (float): Timestep time.
        """
        return self.time

    def setTime(self, time):
        """
        Set time [s].

        Args:
            time (float): Timestep time.
        """
        self.time = time
    
    def getDatetime(self):
        """
        Get date_time.

        Returns:
            date_time (obj): Timestep date_time.
        """
        return self.date_time
    
    def setDatetime(self, date_time):
        """
        Set date_time.

        Args:
            date_time (obj): date_time to set for Timestep.
        """
        self.date_time = date_time
    
    def getJulianDate(self):
        """
        Get julian_date.

        Returns:
            julian_date (float): Julian date.
        """
        return julian.to_jd(self.date_time)
    
    def getSaveFile(self):
        """
        Get save file integer.

        Returns:
            savefile (int): Timestep savefile integer.
        """
        return self.savefile
    
    def setSaveFile(self, savefile):
        """
        Set savefile.

        Args:
            savefile (int): Timestep savefile integer.
        """
        self.savefile = savefile
        
    def setRelationships(self):
        """
        Set parent and universalRF, parentRF, bodyRF relationships.
        """
        self.universalRF = self.reference_frames['UniversalRF']
        for celestial_body in self.celestial_bodies:
            if self.celestial_bodies[celestial_body].parent_name is not None:
                self.celestial_bodies[celestial_body].setParent(self.celestial_bodies[celestial_body].parent_name)
                self.celestial_bodies[celestial_body].setParentRF(self.reference_frames[self.celestial_bodies[celestial_body].parent_name + 'RF'])
            self.celestial_bodies[celestial_body].setUniversalRF(self.universalRF)
            self.celestial_bodies[celestial_body].setBodyRF(self.reference_frames[self.celestial_bodies[celestial_body].name + 'RF'])
            self.celestial_bodies[celestial_body].setBodyFixedRF(self.reference_frames[self.celestial_bodies[celestial_body].name + 'FixedRF'])
        for vessel in self.vessels:
            if self.vessels[vessel].parent_name is not None:
                self.vessels[vessel].setParent(self.celestial_bodies[self.vessels[vessel].parent_name])
                self.vessels[vessel].setParentRF(self.reference_frames[self.vessels[vessel].parent_name + 'RF'])
            self.vessels[vessel].setUniversalRF(self.universalRF)
            self.vessels[vessel].setBodyRF(self.reference_frames[self.vessels[vessel].name + 'RF'])

    def addReferenceFrame(self, reference_frame):
        """
        Add a ReferenceFrame to the Timestep.

        Args:
            reference_frame (obj): ReferenceFrame object to add to Timestep.
        """
        self.reference_frames[reference_frame.name] = reference_frame

    def addCelestialBody(self, celestial_body):
        """
        Add a CelestialBody to the Timestep.

        Args:
            celestial_body (obj): CelestialBody object to add to Timestep.
        """
        if celestial_body.parent_name is None: # If there is no parent the body's parentRF is the universalRF
            celestial_body.setParent(None)
            celestial_body.setUniversalRF(self.universalRF)
            celestial_body.setParentRF(self.universalRF)
            celestial_body.setBodyRF(copy.copy(self.universalRF)) # Should be correctly oriented depending on datetime
            celestial_body.bodyRF.setName(celestial_body.name + 'RF')
            self.addReferenceFrame(celestial_body.bodyRF)
            celestial_body.setBodyFixedRF(copy.copy(self.universalRF)) # Should be correctly oriented depending on datetime
            celestial_body.bodyFixedRF.setName(celestial_body.name + 'FixedRF')
            self.addReferenceFrame(celestial_body.bodyFixedRF)
            self.celestial_bodies[celestial_body.name] = celestial_body
        else: # Else the body's parentRF is the parents bodyRF
            if celestial_body.parent_name in self.celestial_bodies:
                celestial_body.setParent(self.celestial_bodies[celestial_body.parent_name])
                celestial_body.setUniversalRF(self.universalRF)
                celestial_body.setParentRF(celestial_body.parent.bodyRF)
                celestial_body.setBodyRF(copy.copy(celestial_body.parent.bodyRF))
                celestial_body.bodyRF.setName(celestial_body.name + 'RF') # Should be correctly oriented depending on datetime
                self.addReferenceFrame(celestial_body.bodyRF)
                celestial_body.setBodyFixedRF(copy.copy(celestial_body.parent.bodyRF)) # Should be correctly oriented depending on datetime
                celestial_body.bodyFixedRF.setName(celestial_body.name + 'FixedRF')
                self.addReferenceFrame(celestial_body.bodyFixedRF)
                self.celestial_bodies[celestial_body.name] = celestial_body
            else:
                print('Error: Parent "' + celestial_body.parent_name + '" does not exist. Unable to add "' + celestial_body.name + '" to System.')
        
    def addVessel(self, vessel):
        """
        Add a Vessel to the Timestep.

        Args:
            vessel (obj): Vessel object to add to Timestep.
        """
        if vessel.parent_name is None: # If there is no parent the body's parentRF is the universalRF
            vessel.setParent(None)
            vessel.setUniversalRF(self.universalRF)
            vessel.setParentRF(self.universalRF)
            vessel.setBodyRF(copy.copy(self.universalRF))
            vessel.bodyRF.setName(vessel.name + 'RF')
            self.addReferenceFrame(vessel.bodyRF)
            vessel.initPosition()
            self.vessels[vessel.name] = vessel
        else: # Else the body's parentRF is the parents bodyRF
            if vessel.parent_name in self.celestial_bodies:
                vessel.setParent(self.celestial_bodies[vessel.parent_name])
                vessel.setUniversalRF(self.universalRF)
                vessel.setParentRF(vessel.parent.bodyRF)
                vessel.setBodyRF(copy.copy(vessel.parent.bodyRF))
                vessel.bodyRF.setName(vessel.name + 'RF')
                self.addReferenceFrame(vessel.bodyRF)
                vessel.initPosition()
                self.vessels[vessel.name] = vessel
            else:
                print('Error: Parent "' + vessel.parent_name + '" does not exist. Unable to add "' + vessel.name + '" to System.')
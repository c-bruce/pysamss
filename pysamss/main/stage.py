# Date: 06/01/2019
# Author: Callum Bruce
# Stage Class
import numpy as np

class Stage:
    """
    Stage class.

    Args:
        mass (float): Stage mass (kg).
        radius (float): Stage radius (m).
        length (float): Stage length (m).
        position (np.array): Stage position relative to Vessel bodyRF np.array([x,y,z]) (m).

    Note:
        - Stage objects are assumed cylindrical with CoT 0.5 * length aft of
          position.
        - drymass = 0.05 * mass, wetmass = 0.95 * mass.
    """
    def __init__(self, mass=0.0, radius=0.0, length=0.0, position=None):
        self.mass = mass
        self.drymass = 0.05 * mass
        self.wetmass = 0.95 * mass
        self.radius = radius
        self.length = length
        self.position = position
        self.gimbal = np.array([0, 0]) # np.array([theta, psi])

    def save(self, group):
        """
        Save Stage object to .h5 file.

            Args:
                group (h5py group): HDF5 file group to save Stage object to.
        """
        # Save attributes
        group.attrs.create('mass', self.mass)
        group.attrs.create('radius', self.radius)
        group.attrs.create('length', self.length)
        group.create_dataset('position', data=self.position)
        group.attrs.create('drymass', self.drymass)
        group.attrs.create('wetmass', self.wetmass)
        group.create_dataset('gimbal', data=self.gimbal)

    def load(self, group):
        """
        Load Stage object from .h5 file.

            Args:
                group (h5py group): HDF5 file group to save Stage object from.
        """
        # Get/set data
        self.setMass(group.attrs['mass'])
        self.setRadius(group.attrs['radius'])
        self.setLength(group.attrs['length'])
        self.setPostion(np.array(group.get('position')))
        self.setDryMass(group.attrs['drymass'])
        self.setWetMass(group.attrs['wetmass'])
        self.setGimbal(gimbal = np.array(group.get('gimbal')))

    def getMass(self):
        """
        Get stage mass.

        Returns:
            mass (float): Stage mass.
        """
        return self.mass

    def setMass(self, mass):
        """
        Set stage mass.

        Args:
            mass (float): Stage mass.
        """
        self.mass = mass

    def getDryMass(self):
        """
        Get stage drymass.

        Returns:
            drymass (float): Stage drymass.
        """
        return self.drymass

    def setDryMass(self, drymass):
        """
        Set stage drymass.

        Args:
            drymass (float): Stage drymass.
        """
        self.drymass = drymass

    def getWetMass(self):
        """
        Get stage wetmass.

        Returns:
            wetmass (float): Stage wetmass.
        """
        return self.wetmass

    def setWetMass(self, wetmass):
        """
        Set stage wetmass.

        Args:
            wetmass (float): Stage wetmass.
        """
        self.wetmass = wetmass

    def updateMass(self, m_dot):
        """
        Update wetmass and mass due to fuel burn m_dot.

        Args:
            m_dot (float): Mass delta -ive denotes fuel burnt.
        """
        if self.wetmass > 0:
            self.wetmass += m_dot
            self.setMass(self.drymass + self.wetmass)
    
    def getRadius(self):
        """
        Get Stage radius.

        Returns:
            radius (float): Stage radius.
        """
        return self.radius
    
    def setRadius(self, radius):
        """
        Set Stage radius.

        Args:
            radius (float): Stage radius.
        """
        self.radius = radius
    
    def getLength(self):
        """
        Get Stage length.

        Returns:
            length (float): Stage length.
        """
        return self.length
    
    def setLength(self, length):
        """
        Set Stage length.

        Args:
            length (float): Stage length.
        """
        self.length = length
    
    def getPosition(self):
        """
        Get Stage position.

        Returns:
            position (np.array): Stage position relative to Vessel bodyRF np.array([x,y,z]).
        """
        return self.position
    
    def setPostion(self, position):
        """
        Set Stage position.

        Args:
            position (np.array): Stage position relative to Vessel bodyRF np.array([x,y,z]).
        """
        self.position = position
    
    def getGimbal(self):
        """
        Get Stage gimbal.

        Returns:
            gimbal (np.array): Stage gimbal np.array([theta, psi])
        """
        return self.gimbal
    
    def setGimbal(self, gimbal):
        """
        Set Stage gimbal.

        Args:
            gimbal (np.array): Stage gimbal np.array([theta, psi])
        """
        self.gimbal = gimbal

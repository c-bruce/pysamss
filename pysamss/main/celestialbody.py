# Date: 06/01/2019
# Author: Callum Bruce
# CelestialBody Class
import numpy as np
import copy
from .rigidbody import RigidBody
from .referenceframe import ReferenceFrame
from ..helpermath.helpermath import *

class CelestialBody(RigidBody):
    """
    CelestialBody class.

    Args:
        name (str): CelestialBody name.
        mass (float): CelestialBody mass (kg).
        radius (float): CelestialBody radius (m).
        state (np.array): State vector [u, v, w, x, y, z, phi_d, theta_d, psi_d, qw, qx, qy, qz].
        U (np.array): U vector [Fx, Fy, Fz, Mx, My, Mz].
        parent_name (str): Name of parent RigidBody object.
    """
    def __init__(self, name=None, mass=0.0, radius=0.0, state=None, U=None, parent_name=None):
        RigidBody.__init__(self, name=name, state=state, U=U, parent_name=parent_name)
        self.mass = mass
        self.radius = radius
        self.I = self.calculateI()
    
    def save(self, group):
        """
        Save CelestialBody object to .h5 file.

            Args:
                group (h5py group): HDF5 file group to save CelestialBody object to.
        """
        # Save attributes
        group.attrs.create('name', np.string_(self.name))
        group.attrs.create('mass', self.mass)
        group.attrs.create('radius', self.radius)
        group.create_dataset('state', data=self.state)
        group.create_dataset('U', data=self.U)
        if self.parent_name is None:
            group.attrs.create('parent_name', np.string_('None'))
        else:
            group.attrs.create('parent_name', np.string_(self.parent.name))
        group.create_dataset('I', data=self.I)

    def load(self, group):
        """
        Load CelestialBody object from .h5 file.

            Args:
                group (h5py group): HDF5 file group to load CelestialBody object from.
        """
        # Get/set data
        self.setName(group.attrs['name'].decode('UTF-8'))
        self.setMass(group.attrs['mass'])
        self.setRadius(group.attrs['radius'])
        self.setState(np.array(group.get('state')))
        self.setU(np.array(group.get('U')))
        parent_name = group.attrs['parent_name'].decode('UTF-8')
        if parent_name == 'None':
            parent_name = None
        self.setParentName(parent_name)
    
    def getRadius(self):
        """
        Get radius.

        Returns:
            radius (float): CelestialBody radius.
        """
        return self.radius
    
    def setRadius(self, radius):
        """
        Set radius.

        Args:
            radius (float): CelestialBody radius.
        """
        self.radius = radius

    def calculateI(self):
        """
        Calculate intertia matrix I.

        Returns:
            I (np.array): Calculated CelestialBody inertia matrix.
        """
        I = np.array([[(2 / 5) * self.mass * self.radius**2, 0.0, 0.0],
                      [0.0, (2 / 5) * self.mass * self.radius**2, 0.0],
                      [0.0, 0.0, (2 / 5) * self.mass * self.radius**2]])
        return I
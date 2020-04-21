# Date: 06/01/2019
# Author: Callum Bruce
# CelestialBody Class
import numpy as np
import os
import copy
from tvtk.api import tvtk # python wrappers for the C++ vtk ecosystem
import shutil
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
        self.texture = None
        self.actor = self.setActor()
    
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
        if self.texture is None:
            group.attrs.create('texture', np.string_('None'))
        else:
            group.attrs.create('texture', np.string_(self.name + '_texture.jpg'))

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
        texture = group.attrs['texture'].decode('UTF-8')
        if texture == 'None':
            self.texture = None
        else:
            self.setTexture(texture)
        self.setActor()
    
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
    
    def getTexture(self):
        """
        Get texture.

        Returns:
            texture (tvtk.Texture): CelestialBody texture.
        """
        return self.texture

    def setTexture(self, image):
        """
        Set CelestialBody tvtk texture.

        Args:
            image (string): String specifying .jpeg for body texture.
        """
        if not(os.path.exists(self.name + '_texture.jpg')):
            shutil.copyfile(image, self.name + '_texture.jpg')
        img = tvtk.JPEGReader()
        img.file_name = self.name + '_texture.jpg'
        self.texture = tvtk.Texture(input_connection=img.output_port, interpolate=1)
        self.setActor()
    
    def getActor(self):
        """
        Get CelestialBody tvtk actor.
        """
        return self.actor

    def setActor(self):
        """
        Set CelestialBody tvtk actor.

        Note:
            -   Defaults to a white sphere if self.texture is None.
        """
        Nrad = 180
        position = self.getPosition()
        attitude = quaternion2euler(self.getAttitude())
        if self.texture is None:
            p = tvtk.Property(color=(1, 1, 1))
            sphere = tvtk.SphereSource(radius=self.radius, theta_resolution=Nrad, phi_resolution=Nrad)
            sphere_mapper = tvtk.PolyDataMapper(input_connection=sphere.output_port) # Pipeline - mapper
            sphere_actor = tvtk.Actor(mapper=sphere_mapper, property=p) # Pipeline - actor
        else:
            sphere = tvtk.TexturedSphereSource(radius=self.radius, theta_resolution=Nrad, phi_resolution=Nrad) # Pipeline - source
            sphere_mapper = tvtk.PolyDataMapper(input_connection=sphere.output_port) # Pipeline - mapper
            sphere_actor = tvtk.Actor(mapper=sphere_mapper, texture=self.texture, orientation=attitude) # Pipeline - actor
        sphere_actor.add_position(position) # Pipeline - actor.add_position
        self.actor = sphere_actor
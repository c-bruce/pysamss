# Date: 02/04/2019
# Author: Callum Bruce
# Plotting functions
from mayavi import mlab
from tvtk.api import tvtk # python wrappers for the C++ vtk ecosystem
import numpy as np
## See www.cgtrader.com for textures ###

def plotCelestialBody(figure, radius, position, image):
    """
    Plot body and map texture to sphere using mayavi and tvtk.

    Args:
        figure (mlab.figure): Mayavi figure for plot.
        radius (float): Radius of body.
        position (list): Body position [x, y, z].
        image (string): String specifying .jpeg for body texture.
    """
    # Step 1: Load and map texture
    img = tvtk.JPEGReader()
    img.file_name = image
    texture = tvtk.Texture(input_connection=img.output_port, interpolate=1)
    # Step 2: Create a TexturedSphereSource with a given radius and angular resolution
    Nrad = 180
    sphere = tvtk.TexturedSphereSource(radius=radius, theta_resolution=Nrad, phi_resolution=Nrad) # Pipeline - source
    sphere_mapper = tvtk.PolyDataMapper(input_connection=sphere.output_port) # Pipeline - mapper
    sphere_actor = tvtk.Actor(mapper=sphere_mapper, texture=texture, orientation=[0, 0, 180]) # Pipeline - actor
    sphere_actor.add_position((position[0], position[1], position[2])) # Pipeline - actor.add_position
    # Step 3: Add actor to figure
    figure.scene.add_actor(sphere_actor)

def plotTrajectory(figure, points, color):
    """
    Plot trajectory using mayavi and tvtk.

    Args:
        figure (mlab.figure): Mayavi figure for plot.
        points (list): List of points defining trajectory.
        color (tuple): Tuple defining path color, i.e (0, 0, 0).
    """
    line = tvtk.LineSource(points=points)
    line_mapper = tvtk.PolyDataMapper(input_connection=line.output_port)
    p = tvtk.Property(line_width=2, color=color)
    line_actor = tvtk.Actor(mapper=line_mapper, property=p)
    figure.scene.add_actor(line_actor)

def plotCylinder(figure, radius, height, center):
    """
    Plot cylinder using mayavi and tvtk.

    Args:
        figure (mlab.figure): Mayavi figure for plot.
        radius (float): Cylinder radius (m).
        height (float): Cylinder height (m).
        center (list): Cylinder center [x, y, z] (m).
    """
    cylinder = tvtk.CylinderSource(radius=radius, height=height, center=[-center[1], center[0], center[2]], resolution=90)
    cylinder_mapper = tvtk.PolyDataMapper(input_connection=cylinder.output_port)
    cylinder_actor = tvtk.Actor(mapper=cylinder_mapper, orientation=[0, 0, -90])
    figure.scene.add_actor(cylinder_actor)

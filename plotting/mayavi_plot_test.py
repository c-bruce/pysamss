from mayavi import mlab
from tvtk.api import tvtk # python wrappers for the C++ vtk ecosystem
import numpy as np
## See www.cgtrader.com for textures ###
def plotBody(figure, radius, position, image):
    """
    Plot body and map texture to sphere using mayavi and tvtk.

    Args:
        figure (mlab.figure): Mayavi figure for plot.
        radius (float): Radius of body.
        position (list): Body position [x, y, z].
        image (string): String specifying .jpeg for body texture.
    """
    # Load and map texture
    img = tvtk.JPEGReader()
    img.file_name = image
    texture = tvtk.Texture(input_connection=img.output_port, interpolate=1)
    # Create a TexturedSphereSource with a given radius and angular resolution
    Nrad = 180
    sphere = tvtk.TexturedSphereSource(radius=radius, theta_resolution=Nrad, phi_resolution=Nrad) # Pipeline - source
    sphere_mapper = tvtk.PolyDataMapper(input_connection=sphere.output_port) # Pipeline - mapper
    sphere_actor = tvtk.Actor(mapper=sphere_mapper, texture=texture) # Pipeline - actor
    sphere_actor.add_position((position[0],position[1],position[2])) # Pipeline - actor.add_position
    # Add actor to figure
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

# Define figure
figure = mlab.figure(size=(600, 600))

# Plot earth
earthImageFile = 'earth.jpg'
earthPosition = [0, 0, 0]
earthRadius = 6.371e6
plotBody(figure, earthRadius, earthPosition, earthImageFile)

# Plot trajectory
points = np.load('iss_points.npy')
color = (1, 1, 1)
plotTrajectory(figure, points, color)

'''
Note: Can animate rotating Earth by looping...
sphere_actor.add_orientation((0,0,5))
fig.scene.add_actor(sphere_actor)
...every n seconds
'''

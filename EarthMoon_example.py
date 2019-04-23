# Date: 27/01/2019
# Author: Callum Bruce
# Earth - Moon example

import numpy as np
from mayavi import mlab
from time import time
from main import CelestialBody
from helpermath import *
from forcetorque import gravity, thrust
from simulate import simulate, euler
from plotting import plotCelestialBody, plotTrajectory
from pyquaternion import Quaternion

startTime = time()

# Define Earth
earth = CelestialBody(5.972e24, 6.371e6)

# Define Moon
moon = CelestialBody(7.348e22, 1.737e6, parent=earth)
moon.setPosition([3.84402e8, 0, 0])
moon.setVelocity([0, 1022, 0])
moon.setAttitude(euler2quaternion(np.rad2deg([0, 45, 0])))

# earth, moon Initial Forces
gravityForce = gravity(earth, moon)
earth.addForce(-gravityForce)
moon.addForce(gravityForce)

# Simulation loop
dt = 60
t = np.array([0])
for i in range(0,39312):
    t = np.append(t, t[i]+dt)

    # Simulate earth
    simulate(earth, euler, dt)

    # Simulate moon
    simulate(moon, euler, dt)

    # Get forces
    gravityForce = gravity(earth, moon)

    # Add forces
    earth.addForce(-gravityForce)
    moon.addForce(gravityForce)

# Plotting
earthPositions = np.array(earth.state)[:,3:6]
moonPositions = np.array(moon.state)[:,3:6]

figure = mlab.figure(size=(600, 600))

earthImageFile = 'plotting/earth.jpg'
plotCelestialBody(figure, earth.getRadius(), earth.getPosition(), earthImageFile)
plotTrajectory(figure, earthPositions, (1, 1, 1))
earth.bodyRF.plot(figure, earth.getPosition(), scale_factor=earth.radius*1.5)

moonImageFile = 'plotting/moon.jpg'
plotCelestialBody(figure, moon.getRadius(), moon.getPosition(), moonImageFile)
plotTrajectory(figure, moonPositions, (1, 1, 1))
moon.bodyRF.plot(figure, moon.getPosition(), scale_factor=moon.radius*1.5)

mlab.view(focalpoint=moon.getPosition(), figure=figure)

# Date: 06/01/2019
# Author: Callum Bruce
# Orbital ISS example
import numpy as np
from mayavi import mlab
from rocketsim import *

# Define Earth
earth = CelestialBody('Earth', 5.972e24, 6.371e6)

# Define ISS
# See https://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/orbit/ISS/SVPOST.html
stage1 = Stage(415699, 1, 10, [0, 0, 0])
iss = Vessel('ISS', [stage1], parent=earth)
iss.setPosition([-4201711.07, 545774.11, -5320140.96])
iss.setVelocity([-1259.409615, -7539.787624, 218.310203])

# Setup System
system = System()
system.addCelestialBody(earth)
system.addVessel(iss)
system.set_dt(0.1)
system.set_endtime(5561.0)
system.simulateSystem()
'''
# Simulation loop
dt = 0.1
t = np.array([0])

# iss Initial Forces
gravityForce = gravity(earth, iss)
iss.addForce(gravityForce)

for i in range(0, 55610):
    t = np.append(t, t[i]+dt)

    # Simulate iss
    simulate(iss, euler, dt)

    # Calculate forces and torques acting on iss
    gravityForce = gravity(earth, iss)
    iss.addForce(gravityForce)
'''
# Plotting
issPositions = np.array(iss.state)[:,3:6]

figure = mlab.figure(size=(600, 600))

earthImageFile = 'rocketsim/plotting/earth.jpg'
plotCelestialBody(figure, earth.getRadius(), earth.getPosition(), earthImageFile)
plotTrajectory(figure, issPositions, (1, 1, 1))

northeastdownRF = iss.getNorthEastDownRF()
northeastdownRF.plot(figure, iss.getPosition(), scale_factor=100000)

mlab.view(focalpoint=iss.getPosition(), figure=figure)

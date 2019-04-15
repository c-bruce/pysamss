# Date: 06/01/2019
# Author: Callum Bruce
# Orbital ISS example

import numpy as np
from mayavi import mlab
from main import ReferenceFrame, CelestialBody, Stage, Vessel
from forcetorque import gravity, thrust
from simulate import simulate, euler
from plotting import plotCelestialBody, plotTrajectory

# Define Earth
earth = CelestialBody(5.972e24, 6.371e6)

# Define ISS
stage1 = Stage(419725, 1, 10, [0, 0, 0])
iss = Vessel([stage1], parent=earth)
iss.setPosition([earth.radius + 404000, 0, 0])
#iss.setVelocity([0, 7660, 0])
iss.setVelocity([0, 7000, 4000])

# Simulation loop
dt = 0.1
t = np.array([0])

# iss Initial Forces
gravityForce = gravity(earth, iss)
iss.addForce(gravityForce)

for i in range(0,55610):
    t = np.append(t,t[i]+dt)

    # Simulate iss
    simulate(iss, euler, dt)

    # Calculate forces and torques acting on iss
    gravityForce = gravity(earth, iss)
    iss.addForce(gravityForce)

# Plotting
issPositions = np.array(iss.state)[:,3:6]

figure = mlab.figure(size=(600, 600))

earthImageFile = 'plotting/earth.jpg'
plotCelestialBody(figure, earth.getRadius(), earth.getPosition(), earthImageFile)
plotTrajectory(figure, issPositions, (1, 1, 1))

northeastdownRF = iss.getNorthEastDownRF()
northeastdownRF.plot(figure, iss.getPosition(), scale_factor=100000)

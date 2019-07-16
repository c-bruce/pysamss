# Date: 06/01/2019
# Author: Callum Bruce
# Orbital ISS example
import numpy as np
from mayavi import mlab
from rocketsim import *

# Define Earth
earth = CelestialBody('Earth', 5.972e24, 6.371e6)

# Define ISS
"""
See https://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/orbit/ISS/SVPOST.html
See https://celestrak.com/NORAD/elements/stations.txt
ISS (ZARYA)
1 25544U 98067A   19197.73699074  .00000224  00000-0  11644-4 0  9990
2 25544  51.6432 214.6630 0006951 146.0156 190.2537 15.50981102179836
"""
line1 = "1 25544U 98067A   19197.73699074  .00000224  00000-0  11644-4 0  9990"
line2 = "2 25544  51.6432 214.6630 0006951 146.0156 190.2537 15.50981102179836"

a, e, omega, LAN, i, M0, t0, t = twoline2orbitalelements(line1, line2, earth)

iss_position, iss_velocity = orbitalelements2cartesian(a, e, omega, LAN, i, M0, t0, t, earth)

stage1 = Stage(415699, 1, 10, [0, 0, 0])
iss = Vessel('ISS', [stage1], parent=earth)
iss.setPosition(iss_position)
iss.setVelocity(iss_velocity)

# Setup System
system = System()
system.addCelestialBody(earth)
system.addVessel(iss)
system.set_dt(0.1)
system.set_endtime(5561.0)
system.simulateSystem()

# Plotting
issPositions = np.array(iss.state)[:,3:6]

figure = mlab.figure(size=(600, 600))

earthImageFile = 'rocketsim/plotting/earth.jpg'
plotCelestialBody(figure, earth.getRadius(), earth.getPosition(), earthImageFile)
plotTrajectory(figure, issPositions, (1, 1, 1))

northeastdownRF = iss.getNorthEastDownRF()
northeastdownRF.plot(figure, iss.getPosition(), scale_factor=100000)

mlab.view(focalpoint=iss.getPosition(), figure=figure)

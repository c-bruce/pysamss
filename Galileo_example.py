# Date: 06/01/2019
# Author: Callum Bruce
# Galileo constellation example
import numpy as np
from mayavi import mlab
from rocketsim import *

# Setup System
system = System()

# Define Earth
earth = CelestialBody('Earth', 5.972e24, 6.371e6)
system.addCelestialBody(earth)

# Load in TLE data to define constellation
f = open("rocketsim/resources/GalileoConstellation_TLE.txt", "r")
gc_TLE = f.read()
gc_TLE = gc_TLE.split("\n")[0:-1]
f.close()

for i in range(0,26):
    # Define satellite
    # https://en.wikipedia.org/wiki/Galileo_%28satellite_navigation%29
    name = gc_TLE[i * 3]
    line1 = gc_TLE[(i * 3) + 1]
    line2 = gc_TLE[(i * 3) + 2]
    stage = Stage(675, 0.6, 2.7, [0, 0, 0])
    gsat = Vessel(name, [stage], parent=earth)
    a, e, omega, LAN, i, M0, t0, t = twoline2orbitalelements(line1, line2, earth)
    position, velocity = orbitalelements2cartesian(a, e, omega, LAN, i, M0, t0, t, earth)
    gsat.setPosition(position)
    gsat.setVelocity(velocity)
    system.addVessel(gsat)

system.set_dt(10)
system.set_endtime(50820.0)
system.simulateSystem()

# Plotting
figure = mlab.figure(size=(600, 600))
earthImageFile = 'rocketsim/plotting/earth.jpg'
plotCelestialBody(figure, earth.getRadius(), earth.getPosition(), earthImageFile)

for gsat in system.vessels.values():
    positions = np.array(gsat.state)[:,3:6]
    plotTrajectory(figure, positions, (1, 1, 1))
    northeastdownRF = gsat.getNorthEastDownRF()
    northeastdownRF.plot(figure, gsat.getPosition(), scale_factor=100000)

#mlab.view(focalpoint=iss.getPosition(), figure=figure)

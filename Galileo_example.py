# Date: 06/01/2019
# Author: Callum Bruce
# Galileo constellation example
import numpy as np
import urllib3
from mayavi import mlab
from pysamss import *

# Step 1: Setup System
system = System('Galileo')

# Step 2: Define Earth
earth = CelestialBody('Earth', 5.972e24, 6.371e6)
system.current.addCelestialBody(earth)

# Step 3: Get TLE data for Galileo Constelation
http = urllib3.PoolManager()
tle = http.request('GET', 'https://www.celestrak.com/NORAD/elements/galileo.txt')
tle = tle.data.decode('utf-8').strip().split('\r\n') # Gets full TLE's for constelation into a list

# Step 4: Define satellites and add to system
# https://en.wikipedia.org/wiki/Galileo_%28satellite_navigation%29
for i in range(0, int(len(tle)/3)):
    name = tle[i * 3]
    line1 = tle[(i * 3) + 1]
    line2 = tle[(i * 3) + 2]
    stage = Stage(675, 0.6, 2.7, np.array([0, 0, 0]))
    gsat = Vessel(name, [stage], parent_name='Earth')
    a, e, omega, LAN, i, M0, t0, t = twoline2orbitalelements(line1, line2, earth)
    position, velocity = orbitalelements2cartesian(a, e, omega, LAN, i, M0, t0, t, earth)
    gsat.setPosition(position)
    gsat.setVelocity(velocity)
    system.current.addVessel(gsat)

# Step 5: Simulate system
system.setDt(10)
system.setEndTime(50820.0)
system.setSaveInterval(10)
system.simulateSystem()

# Step 6: Post Processing
# Step 6.1: Load data
system.load('Galileo.psm')

# Step 6.2 Plotting
figure = mlab.figure(size=(600, 600))
earthImageFile = 'pysamss/plotting/earth.jpg'
earth = system.current.celestial_bodies['Earth']
plotCelestialBody(figure, earth.getRadius(), earth.getPosition(), earthImageFile)

timesteps = sorted(list(system.timesteps.keys()))
gsats = system.current.vessels.keys()
for gsat in gsats:
    positions = np.empty([len(timesteps), 3])
    for i in range(0, len(timesteps)):
        positions[i,:] = system.timesteps[timesteps[i]].vessels[gsat].getPosition()
    plotTrajectory(figure, positions, (1, 1, 1))
    northeastdownRF = system.timesteps[timesteps[i]].vessels[gsat].getNorthEastDownRF()
    northeastdownRF.plot(figure, system.timesteps[timesteps[i]].vessels[gsat].getPosition(), scale_factor=100000)

mlab.show()
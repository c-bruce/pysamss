# Date: 06/01/2019
# Author: Callum Bruce
# Galileo constellation example
import numpy as np
import urllib3
from mayavi import mlab
from pysamss import *
from sgp4.api import Satrec

# Step 1: Setup System
system = System('Galileo')
system.current.setDatetime(datetime.datetime.utcnow()) # Set current time utc

# Step 2: Define Earth
earth = CelestialBody('Earth', 5.972e24, 6.371e6)
system.current.addCelestialBody(earth)
system.current.celestial_bodies['Earth'].setTexture('pysamss/resources/earth.jpg')

# Step 3: Get TLE data for Galileo Constelation
#time = system.current.getJulianDate()
time = np.modf(system.current.getJulianDate()) # Split Julian date into integer and decimal for spg4 library
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
    # Using pysamss methods
    #a, e, omega, LAN, i, M0, t0, t = twoline2orbitalelements(line1, line2, earth)
    #position, velocity = orbitalelements2cartesian(a, e, omega, LAN, i, M0, t0, time, earth)
    # Using spg4 methods
    sat = Satrec.twoline2rv(line1, line2)
    e, pos, vel = sat.sgp4(time[1], time[0])
    pos = np.array(pos) * 1000
    vel = np.array(vel) * 1000
    gsat.setPosition(pos)
    gsat.setVelocity(vel)
    system.current.addVessel(gsat)

# Step 5: Simulate system
system.setDt(10)
system.setEndTime(50820.0)
system.setSaveInterval(10)
system.simulateSystem()

# Step 6: Post processing
system.load('Galileo.psm')
fig = MainWidget()
fig.loadSystem(system)
fig.showMaximized()
mlab.show()
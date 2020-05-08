# Date: 07/05/2020
# Author: Callum Bruce
# Spire constellation example.
import numpy as np
from mayavi import mlab
import datetime
import urllib3
from sgp4.api import Satrec
import pysamss

# Step 1: Setup System
system = pysamss.System('Spire')
system.current.setDatetime(datetime.datetime.utcnow()) # Set current time utc

# Step 2: Define Earth
system.current.addCelestialBody(pysamss.CelestialBody('Earth', 5.972e24, 6.371e6))
system.current.celestial_bodies['Earth'].setAttitudeDot(np.array([0.0, 0.0, np.deg2rad(360 / ((23 * 60 * 60) + (56 * 60) + 4))]))
system.current.celestial_bodies['Earth'].setTexture(pysamss.__file__[:-12] + '/resources/earth.jpg')

# Step 3: Get TLE data for Galileo Constelation
#time = system.current.getJulianDate()
time = np.modf(system.current.getJulianDate()) # Split Julian date into integer and decimal for spg4 library
http = urllib3.PoolManager()
tle = http.request('GET', 'https://celestrak.com/NORAD/elements/spire.txt')
tle = tle.data.decode('utf-8').strip().split('\r\n') # Gets full TLE's for constelation into a list

# Step 4: Define satellites and add to system
# https://spire.com/spirepedia/low-earth-multi-use-receiver/
# https://space.skyrocket.de/doc_sdat/lemur-2.htm
for i in range(0, int(len(tle)/3)):
    name = tle[i * 3]
    line1 = tle[(i * 3) + 1]
    line2 = tle[(i * 3) + 2]
    gsat = pysamss.Vessel(name, [pysamss.Stage(4.0, 0.05, 0.345, np.array([0, 0, 0]))], parent_name='Earth')
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
system.setScheme('rk4')
system.setDt(0.1)
system.setEndTime(5561.0)
system.setSaveInterval(10000)
system.simulateSystem()

# Step 6: Post processing
system.load('Spire.psm')
fig = pysamss.MainWidget()
fig.loadSystem(system)
fig.showMaximized()
mlab.show()
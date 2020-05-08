# Date: 06/05/2020
# Author: Callum Bruce
# ISS example.
import numpy as np
from mayavi import mlab
import datetime
import urllib3
from sgp4.api import Satrec
import pysamss

# Step 1: Setup system
system = pysamss.System('EarthISS')
system.current.setDatetime(datetime.datetime.utcnow()) # Set current time utc
# Step 1.1: Add Earth and ISS to system
system.current.addCelestialBody(pysamss.CelestialBody('Earth', 5.972e24, 6.371e6))
system.current.addVessel(pysamss.Vessel('ISS', [pysamss.Stage(419725, 1, 10, np.array([0, 0, 0]))], parent_name='Earth'))

# Step 2: Calculate positions and velocities
#time = system.current.getJulianDate()
time = np.modf(system.current.getJulianDate()) # Split Julian date into integer and decimal for spg4 library
# ISS
http = urllib3.PoolManager()
tle = http.request('GET', 'https://www.celestrak.com/NORAD/elements/stations.txt')
tle = tle.data.decode('utf-8').strip().split('\r\n') # Gets full TLE's for constelation into a list
iss_tle = tle[0:3]
# Using pysamss methods
#a, e, omega, LAN, i, M0, t0, t = twoline2orbitalelements(iss_tle[1], iss_tle[2], system.current.celestial_bodies['Earth'])
#iss_pos, iss_vel = orbitalelements2cartesian(a, e, omega, LAN, i, M0, t0, time, system.current.celestial_bodies['Earth'])
# Using spg4 methods
iss = Satrec.twoline2rv(iss_tle[1], iss_tle[2])
e, iss_pos, iss_vel = iss.sgp4(time[1], time[0])
iss_pos = np.array(iss_pos) * 1000
iss_vel = np.array(iss_vel) * 1000

# Step 3: Set positions and velocities
system.current.celestial_bodies['Earth'].setAttitudeDot(np.array([0.0, 0.0, np.deg2rad(360 / ((23 * 60 * 60) + (56 * 60) + 4))]))
system.current.celestial_bodies['Earth'].setTexture(pysamss.__file__[:-12] + '/resources/earth.jpg')
system.current.vessels['ISS'].setPosition(iss_pos, local=True)
system.current.vessels['ISS'].setVelocity(iss_vel, local=True)

# Step 4: Simulate system
system.setScheme('rk4')
system.setDt(0.1)
system.setEndTime(5561.0)
system.setSaveInterval(10)
system.simulateSystem()

# Step 5: Post processing
system.load('EarthISS.psm')
fig = pysamss.MainWidget()
fig.loadSystem(system)
fig.showMaximized()
mlab.show()
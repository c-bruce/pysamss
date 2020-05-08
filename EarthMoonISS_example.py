# Date: 24/06/2019
# Author: Callum Bruce
# Orbital ISS example including the Earth and Moon. Simulated using System class.
# To run, ensure 'de430.bsp' is downloaded to the working directory. See https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/.
import numpy as np
from mayavi import mlab
from pysamss import *
import datetime
import julian
from jplephem.spk import SPK
import urllib3
from sgp4.api import Satrec

# Step 1: Setup system
system = System('EarthMoonISS')
system.current.setDatetime(datetime.datetime.utcnow()) # Set current time utc
# Step 1.1: Add Earth, Moon and ISS to system
system.current.addCelestialBody(CelestialBody('Earth', 5.972e24, 6.371e6))
system.current.addCelestialBody(CelestialBody('Moon', 7.348e22, 1.737e6, parent_name='Earth'))
system.current.addVessel(Vessel('ISS', [Stage(419725, 1, 10, np.array([0, 0, 0]))], parent_name='Earth'))

# Step 2: Calculate positions and velocities
time = system.current.getJulianDate()
kernel = SPK.open('pysamss/resources/de430.bsp')
earth_pos, earth_vel = kernel[3,399].compute_and_differentiate(time)
# Earth
earth_pos *= 1000 # Convert from km -> m
earth_vel /= 86.4 # Convert from km/day -> m/s
# Moon
moon_pos, moon_vel = kernel[3,301].compute_and_differentiate(time)
moon_pos *= 1000 # Convert from km -> m
moon_vel /= 86.4 # Convert from km/day -> m/s
# ISS
time = np.modf(time) # Split Julian date into integer and decimal for spg4 library
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
system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Earth'].setAttitudeDot(np.array([0.0, 0.0, np.deg2rad(360 / ((23 * 60 * 60) + (56 * 60) + 4))]))
system.current.celestial_bodies['Earth'].setTexture('pysamss/resources/earth.jpg')
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.celestial_bodies['Moon'].setAttitudeDot(np.array([0.0, 0.0, np.deg2rad(360 / 2358720.0)]))
system.current.celestial_bodies['Moon'].setTexture('pysamss/resources/moon.jpg')
system.current.vessels['ISS'].setPosition(iss_pos, local=True)
system.current.vessels['ISS'].setVelocity(iss_vel, local=True)

# Step 4: Simulate system
system.setDt(0.1)
system.setEndTime(5561.0)
system.setSaveInterval(10)
system.simulateSystem()

# Step 5: Post processing
system.load('EarthMoonISS.psm')
fig = MainWidget()
fig.loadSystem(system)
fig.showMaximized()
mlab.show()
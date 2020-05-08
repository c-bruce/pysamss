# Date: 10/01/2020
# Author: Callum Bruce
# Sun, Earth, Moon Example
# To run, ensure 'de430.bsp' is downloaded to the working directory. See https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/.
import numpy as np
from mayavi import mlab
import datetime
from jplephem.spk import SPK
import pysamss

# Step 1: Setup system
system = pysamss.System('SunEarthMoon')
system.current.setDatetime(datetime.datetime.utcnow()) # Set current time utc
# Step 1.1: Add Sun, Earth and Moon to system
system.current.addCelestialBody(pysamss.CelestialBody('Sun', 1.9885e30, 696342e3))
system.current.addCelestialBody(pysamss.CelestialBody('Earth', 5.972e24, 6.371e6, parent_name='Sun'))
system.current.addCelestialBody(pysamss.CelestialBody('Moon', 7.348e22, 1.737e6, parent_name='Earth'))

# Step 2: Calculate positions and velocities
time = system.current.getJulianDate()
kernel = SPK.open('de430.bsp')
# Sun
sun_pos, sun_vel = kernel[0,10].compute_and_differentiate(time)
sun_pos *= 1000 # Convert from km -> m
sun_vel /= 86.4 # Convert from km/day -> m/s
# Earth
earth_pos, earth_vel = np.array(kernel[0,3].compute_and_differentiate(time)) + np.array(kernel[3,399].compute_and_differentiate(time))
earth_pos *= 1000 # Convert from km -> m
earth_vel /= 86.4 # Convert from km/day -> m/s
# Moon
moon_pos, moon_vel = np.array(kernel[0,3].compute_and_differentiate(time)) + np.array(kernel[3,301].compute_and_differentiate(time))
moon_pos *= 1000 # Convert from km -> m
moon_vel /= 86.4 # Convert from km/day -> m/s

# Step 3: Set positions and velocities
system.current.celestial_bodies['Sun'].setPosition(sun_pos)
system.current.celestial_bodies['Sun'].setVelocity(sun_vel)
system.current.celestial_bodies['Sun'].setTexture(pysamss.__file__[:-12] + '/resources/sun.jpg')
system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Earth'].setAttitudeDot(np.array([0.0, 0.0, np.deg2rad(360 / ((23 * 60 * 60) + (56 * 60) + 4))]))
system.current.celestial_bodies['Earth'].setTexture(pysamss.__file__[:-12] + '/resources/earth.jpg')
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.celestial_bodies['Moon'].setAttitudeDot(np.array([0.0, 0.0, np.deg2rad(360 / 2358720.0)]))
system.current.celestial_bodies['Moon'].setTexture(pysamss.__file__[:-12] + '/resources/moon.jpg')

# Step 4: Simulate system
system.setDt(60.0)
system.setEndTime(31536000.0)
system.setSaveInterval(1000)
system.simulateSystem()

# Step 5: Post processing
system.load('SunEarthMoon.psm')
fig = pysamss.MainWidget()
fig.loadSystem(system)
fig.showMaximized()
mlab.show()
# Date: 11/05/2020
# Author: Callum Bruce
# Lunar Reconnaissance Orbiter example including the Earth and Moon.
# To run, ensure 'de430.bsp' is downloaded to the working directory. See https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/.
import numpy as np
from mayavi import mlab
import datetime
from jplephem.spk import SPK
import pysamss

# Step 1: Setup system
system = pysamss.System('EarthMoonLRO')
system.current.setDatetime(datetime.datetime.utcnow()) # Set current time utc
# Step 1.1: Add Earth, Moon and LRO to system
# https://earth.esa.int/web/eoportal/satellite-missions/l/lro
system.current.addCelestialBody(pysamss.CelestialBody('Earth', 5.972e24, 6.371e6))
system.current.addCelestialBody(pysamss.CelestialBody('Moon', 7.348e22, 1.737e6, parent_name='Earth'))
system.current.addVessel(pysamss.Vessel('LRO', [pysamss.Stage(1846, 1, 1, np.array([0, 0, 0]))], parent_name='Moon'))

# Step 2: Calculate positions and velocities
time = system.current.getJulianDate()
kernel = SPK.open('de430.bsp')
# Earth
earth_pos, earth_vel = kernel[3,399].compute_and_differentiate(time)
earth_pos *= 1000 # Convert from km -> m
earth_vel /= 86.4 # Convert from km/day -> m/s
# Moon
moon_pos, moon_vel = kernel[3,301].compute_and_differentiate(time)
moon_pos *= 1000 # Convert from km -> m
moon_vel /= 86.4 # Convert from km/day -> m/s
# LRO
lro_pos = np.array([0.0, 0.0, system.current.celestial_bodies['Moon'].getRadius() + 50000])
lro_vel = np.array([1650.0, 0.0, 0.0])

# Step 3: Set positions and velocities
system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Earth'].setAttitudeDot(np.array([0.0, 0.0, np.deg2rad(360 / ((23 * 60 * 60) + (56 * 60) + 4))]))
system.current.celestial_bodies['Earth'].setTexture(pysamss.__file__[:-12] + '/resources/earth.jpg')
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.celestial_bodies['Moon'].setAttitudeDot(np.array([0.0, 0.0, np.deg2rad(360 / 2358720.0)]))
system.current.celestial_bodies['Moon'].setTexture(pysamss.__file__[:-12] + '/resources/moon.jpg')
system.current.vessels['LRO'].setPosition(lro_pos, local=True)
system.current.vessels['LRO'].setVelocity(lro_vel, local=True)

# Step 4: Simulate system
system.setDt(0.1)
system.setEndTime(13560.0)
system.setSaveInterval(10)
system.simulateSystem()

# Step 5: Post processing
system.load('EarthMoonLRO.psm')
fig = pysamss.MainWidget()
fig.loadSystem(system)
fig.showMaximized()
mlab.show()
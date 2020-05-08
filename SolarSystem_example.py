# Date: 08/05/2020
# Author: Callum Bruce
# Solar System Example.
# To run, ensure 'de430.bsp' is downloaded to the working directory. See https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/.
import numpy as np
from mayavi import mlab
import datetime
from jplephem.spk import SPK
import pysamss

# Step 1: Setup system
system = pysamss.System('SolarSystem')
system.current.setDatetime(datetime.datetime.utcnow()) # Set current time utc
# Step 1.1: Add CelestialBodies to system
# https://en.wikipedia.org/wiki/List_of_Solar_System_objects_by_size
system.current.addCelestialBody(pysamss.CelestialBody('Sun', 1.9885e30, 696342e3))
system.current.addCelestialBody(pysamss.CelestialBody('Mercury', 3.3011e23, 2.4397e6, parent_name='Sun'))
system.current.addCelestialBody(pysamss.CelestialBody('Venus', 4.8675e24, 6.0518e6, parent_name='Sun'))
system.current.addCelestialBody(pysamss.CelestialBody('Earth', 5.972e24, 6.371e6, parent_name='Sun'))
system.current.addCelestialBody(pysamss.CelestialBody('Moon', 7.348e22, 1.737e6, parent_name='Earth'))
system.current.addCelestialBody(pysamss.CelestialBody('Mars', 6.4171e23, 3.3895e6, parent_name='Sun'))
system.current.addCelestialBody(pysamss.CelestialBody('Jupiter', 1.8982e27, 6.9911e7, parent_name='Sun'))
system.current.addCelestialBody(pysamss.CelestialBody('Saturn', 5.6834e26, 5.8232e7, parent_name='Sun'))
system.current.addCelestialBody(pysamss.CelestialBody('Uranus', 8.6810e25, 2.5362e7, parent_name='Sun'))
system.current.addCelestialBody(pysamss.CelestialBody('Neptune', 1.02413e26, 2.4622e7, parent_name='Sun'))

# Step 2: Calculate positions and velocities
time = system.current.getJulianDate()
kernel = SPK.open('de430.bsp')
# Sun
sun_pos, sun_vel = kernel[0,10].compute_and_differentiate(time)
sun_pos *= 1000 # Convert from km -> m
sun_vel /= 86.4 # Convert from km/day -> m/s
# Mercury
mercury_pos, mercury_vel = np.array(kernel[0,1].compute_and_differentiate(time)) + np.array(kernel[1,199].compute_and_differentiate(time))
mercury_pos *= 1000 # Convert from km -> m
mercury_vel /= 86.4 # Convert from km/day -> m/s
# Venus
venus_pos, venus_vel = np.array(kernel[0,2].compute_and_differentiate(time)) + np.array(kernel[2,299].compute_and_differentiate(time))
venus_pos *= 1000 # Convert from km -> m
venus_vel /= 86.4 # Convert from km/day -> m/s
# Earth
earth_pos, earth_vel = np.array(kernel[0,3].compute_and_differentiate(time)) + np.array(kernel[3,399].compute_and_differentiate(time))
earth_pos *= 1000 # Convert from km -> m
earth_vel /= 86.4 # Convert from km/day -> m/s
# Moon
moon_pos, moon_vel = np.array(kernel[0,3].compute_and_differentiate(time)) + np.array(kernel[3,301].compute_and_differentiate(time))
moon_pos *= 1000 # Convert from km -> m
moon_vel /= 86.4 # Convert from km/day -> m/s
# Mars
mars_pos, mars_vel = np.array(kernel[0,4].compute_and_differentiate(time))
mars_pos *= 1000 # Convert from km -> m
mars_vel /= 86.4 # Convert from km/day -> m/s
# Jupiter
jupiter_pos, jupiter_vel = np.array(kernel[0,5].compute_and_differentiate(time))
jupiter_pos *= 1000 # Convert from km -> m
jupiter_vel /= 86.4 # Convert from km/day -> m/s
# Saturn
saturn_pos, saturn_vel = np.array(kernel[0,6].compute_and_differentiate(time))
saturn_pos *= 1000 # Convert from km -> m
saturn_vel /= 86.4 # Convert from km/day -> m/s
# Uranus
uranus_pos, uranus_vel = np.array(kernel[0,7].compute_and_differentiate(time))
uranus_pos *= 1000 # Convert from km -> m
uranus_vel /= 86.4 # Convert from km/day -> m/s
# Neptune
neptune_pos, neptune_vel = np.array(kernel[0,8].compute_and_differentiate(time))
neptune_pos *= 1000 # Convert from km -> m
neptune_vel /= 86.4 # Convert from km/day -> m/s


# Step 3: Set positions and velocities
# Sun
system.current.celestial_bodies['Sun'].setPosition(sun_pos)
system.current.celestial_bodies['Sun'].setVelocity(sun_vel)
system.current.celestial_bodies['Sun'].setTexture(pysamss.__file__[:-12] + '/resources/sun.jpg')
# Mercury
system.current.celestial_bodies['Mercury'].setPosition(mercury_pos)
system.current.celestial_bodies['Mercury'].setVelocity(mercury_vel)
# Venus
system.current.celestial_bodies['Venus'].setPosition(venus_pos)
system.current.celestial_bodies['Venus'].setVelocity(venus_vel)
# Earth
system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Earth'].setAttitudeDot(np.array([0.0, 0.0, np.deg2rad(360 / ((23 * 60 * 60) + (56 * 60) + 4))]))
system.current.celestial_bodies['Earth'].setTexture(pysamss.__file__[:-12] + '/resources/earth.jpg')
# Moon
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.celestial_bodies['Moon'].setAttitudeDot(np.array([0.0, 0.0, np.deg2rad(360 / 2358720.0)]))
system.current.celestial_bodies['Moon'].setTexture(pysamss.__file__[:-12] + '/resources/moon.jpg')
# Mars
system.current.celestial_bodies['Mars'].setPosition(mars_pos)
system.current.celestial_bodies['Mars'].setVelocity(mars_vel)
system.current.celestial_bodies['Mars'].setTexture(pysamss.__file__[:-12] + '/resources/mars.jpg')
# Jupiter
system.current.celestial_bodies['Jupiter'].setPosition(jupiter_pos)
system.current.celestial_bodies['Jupiter'].setVelocity(jupiter_vel)
# Saturn
system.current.celestial_bodies['Saturn'].setPosition(saturn_pos)
system.current.celestial_bodies['Saturn'].setVelocity(saturn_vel)
# Uranus
system.current.celestial_bodies['Uranus'].setPosition(uranus_pos)
system.current.celestial_bodies['Uranus'].setVelocity(uranus_vel)
# Neptune
system.current.celestial_bodies['Neptune'].setPosition(neptune_pos)
system.current.celestial_bodies['Neptune'].setVelocity(neptune_vel)

# Step 4: Simulate system
system.setDt(60.0)
system.setEndTime(31536000.0)
system.setSaveInterval(1000)
system.simulateSystem()

# Step 5: Post processing
system.load('SolarSystem.psm')
fig = pysamss.MainWidget()
fig.loadSystem(system)
fig.showMaximized()
mlab.show()
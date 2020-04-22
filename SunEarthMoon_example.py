# Date: 10/01/2020
# Author: Callum Bruce
# Sun - Earth - Moon Example
import numpy as np
from mayavi import mlab
from pysamss import *
import datetime
import julian
from jplephem.spk import SPK

# Step 1: Setup Celestial Bodies
# Get Sun, Earth and Moon positions and velocity from jplephem
kernel = SPK.open('pysamss/resources/de430.bsp')

time = datetime.datetime.now()
time1 = julian.to_jd(time)
time2 = time1 + 1 / (24 * 60 * 60)

sun_pos1 = kernel[0,10].compute(time1) * 1000
sun_pos2 = kernel[0,10].compute(time2) * 1000
sun_vel = (sun_pos2 - sun_pos1) / 1

earth_pos1 = (kernel[0,3].compute(time1) + kernel[3,399].compute(time1)) * 1000
earth_pos2 = (kernel[0,3].compute(time2) + kernel[3,399].compute(time2)) * 1000
earth_vel = (earth_pos2 - earth_pos1) / 1

moon_pos1 = (kernel[0,3].compute(time1) + kernel[3,301].compute(time1)) * 1000
moon_pos2 = (kernel[0,3].compute(time2) + kernel[3,301].compute(time2)) * 1000
moon_vel = (moon_pos2 - moon_pos1) / 1

# Define Sun
sun = CelestialBody('Sun', 1.9885e30, 696342e3)
#sun.setPosition(sun_pos1)
#sun.setVelocity(sun_vel)

# Define Earth
earth = CelestialBody('Earth', 5.972e24, 6.371e6, parent_name='Sun')
#earth.setPosition(earth_pos1)
#earth.setVelocity(earth_vel)

# Define Moon
moon = CelestialBody('Moon', 7.348e22, 1.737e6, parent_name='Earth')
#moon.setPosition(moon_pos1)
#moon.setVelocity(moon_vel)

# Step 2: Setup and run System
system = System('SunEarthMoon')
system.current.addCelestialBody(sun)
system.current.addCelestialBody(earth)
system.current.addCelestialBody(moon)
system.current.celestial_bodies['Sun'].setPosition(sun_pos1)
system.current.celestial_bodies['Sun'].setVelocity(sun_vel)
system.current.celestial_bodies['Sun'].setTexture('pysamss/resources/sun.jpg')
system.current.celestial_bodies['Earth'].setPosition(earth_pos1)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Earth'].setTexture('pysamss/resources/earth.jpg')
system.current.celestial_bodies['Moon'].setPosition(moon_pos1)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.celestial_bodies['Moon'].setTexture('pysamss/plotting/moon.jpg')
system.setDt(60.0)
system.setEndTime(31536000.0)
system.setSaveInterval(1000)
system.simulateSystem()

# Step 3: Post Processing
# Step 3.1: Load data
system.load('SunEarthMoon.psm')

# Step 3.2: Get Sun, Earth and Moon position data
timesteps = sorted(list(system.timesteps.keys()))
sunPositions = np.empty([len(timesteps), 3])
earthPositions = np.empty([len(timesteps), 3])
moonPositions = np.empty([len(timesteps), 3])
for i in range(0, len(timesteps)):
    sunPositions[i,:] = system.timesteps[timesteps[i]].celestial_bodies['Sun'].getPosition()
    earthPositions[i,:] = system.timesteps[timesteps[i]].celestial_bodies['Earth'].getPosition()
    moonPositions[i,:] = system.timesteps[timesteps[i]].celestial_bodies['Moon'].getPosition()
sun = system.current.celestial_bodies['Sun']
earth = system.current.celestial_bodies['Earth']
moon = system.current.celestial_bodies['Moon']

# Step 3.3: Plotting
figure = mlab.figure(size=(600, 600))

figure.scene.add_actor(sun.actor)
plotTrajectory(figure, sunPositions, (1, 1, 1))
sun.bodyRF.plot(figure, sun.getPosition(), scale_factor=sun.getRadius()*1.5)

figure.scene.add_actor(earth.actor)
plotTrajectory(figure, earthPositions, (1, 1, 1))
earth.bodyRF.plot(figure, earth.getPosition(), scale_factor=earth.getRadius()*1.5)

figure.scene.add_actor(moon.actor)
plotTrajectory(figure, moonPositions, (1, 1, 1))
moon.bodyRF.plot(figure, moon.getPosition(), scale_factor=moon.getRadius()*1.5)

mlab.view(focalpoint=moon.getPosition(), figure=figure)

mlab.show()
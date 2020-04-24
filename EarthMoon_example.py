# Date: 27/01/2019
# Author: Callum Bruce
# Earth - Moon example
import numpy as np
from mayavi import mlab
from pysamss import *
import datetime
import julian
from jplephem.spk import SPK

# Step 1: Setup Celestial Bodies
# Get Earth and Moon positions and velocity from jplephem
kernel = SPK.open('pysamss/resources/de430.bsp')

time = datetime.datetime.now()
time1 = julian.to_jd(time)
time2 = time1 + 1 / (24 * 60 * 60)
earth_pos1 = kernel[3,399].compute(time1) * 1000
earth_pos2 = kernel[3,399].compute(time2) * 1000
earth_vel = (earth_pos2 - earth_pos1) / 1

moon_pos1 = kernel[3,301].compute(time1) * 1000
moon_pos2 = kernel[3,301].compute(time2) * 1000
moon_vel = (moon_pos2 - moon_pos1) / 1

# Define Earth
earth = CelestialBody('Earth', 5.972e24, 6.371e6)

# Define Moon
moon = CelestialBody('Moon', 7.348e22, 1.737e6, parent_name='Earth')

# Step 2: Setup and run System
system = System('EarthMoon')
#system.setTexture('pysamss/resources/starmap_galactic.jpg')
system.current.addCelestialBody(earth)
system.current.addCelestialBody(moon)
system.current.celestial_bodies['Earth'].setPosition(earth_pos1)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Earth'].setAttitudeDot(np.array([0.0, 0.0, np.deg2rad(360/((23*60*60) + (56*60) + 4))]))
system.current.celestial_bodies['Earth'].setTexture('pysamss/resources/earth.jpg')
system.current.celestial_bodies['Moon'].setPosition(moon_pos1)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.celestial_bodies['Moon'].setTexture('pysamss/resources/moon.jpg')
system.setDt(60.0)
system.setEndTime(2358720.0)
system.setSaveInterval(100)
system.simulateSystem()

# Step 3: Post Processing
# Step 3.1: Load data
system.load('EarthMoon.psm')

# Step 3.2: Get Earth, Moon and ISS position data
timesteps = sorted(list(system.timesteps.keys()))
earthPositions = np.empty([len(timesteps), 3])
moonPositions = np.empty([len(timesteps), 3])
for i in range(0, len(timesteps)):
    earthPositions[i,:] = system.timesteps[timesteps[i]].celestial_bodies['Earth'].getPosition()
    moonPositions[i,:] = system.timesteps[timesteps[i]].celestial_bodies['Moon'].getPosition()
earth = system.current.celestial_bodies['Earth']
moon = system.current.celestial_bodies['Moon']

# Step 3.3: Plotting
figure = mlab.figure(size=(600, 600))

#figure.scene.add_actor(system.actor)

figure.scene.add_actor(earth.actor)
plotTrajectory(figure, earthPositions, (1, 1, 1))
earth.bodyRF.plot(figure, earth.getPosition(), scale_factor=earth.getRadius()*1.5)

figure.scene.add_actor(moon.actor)
plotTrajectory(figure, moonPositions, (1, 1, 1))
moon.bodyRF.plot(figure, moon.getPosition(), scale_factor=moon.getRadius()*1.5)

mlab.view(focalpoint=earth.getPosition(), figure=figure)

mlab.show()

def updateScene(timestep_int):
    keys = list(system.timesteps.keys())
    keys.sort()
    # Remove old actor(s)
    figure.scene.remove_actor(system.timesteps[keys[timestep_int-1]].celestial_bodies['Earth'].actor)
    # Define and add new actor(s)
    earthactor = system.timesteps[keys[timestep_int]].celestial_bodies['Earth'].actor
    figure.scene.add_actor(earthactor)
    mlab.view(focalpoint=system.timesteps[keys[timestep_int]].celestial_bodies['Earth'].getPosition(),
              distance=system.timesteps[keys[timestep_int]].celestial_bodies['Earth'].getRadius()*5,
              figure=figure)

figure = mlab.figure(size=(600, 600))
figure.scene.add_actor(system.timesteps[0.0].celestial_bodies['Earth'].actor)
for i in range(1,394):
    updateScene(i)
    input('Press any key...')

# Date: 24/06/2019
# Author: Callum Bruce
# Orbital ISS example including the Earth and Moon. Simulated using System class.
import numpy as np
from mayavi import mlab
from pysamss import *
import datetime
import julian
from jplephem.spk import SPK

# Step 1: Setup Celestial Bodies and Vessels
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

# Define ISS
stage1 = Stage(419725, 1, 10, np.array([0, 0, 0]))
iss = Vessel('ISS', [stage1], parent_name='Earth')

# Step 2: Setup and run System
system = System('EarthMoonISS')
system.current.addCelestialBody(earth)
system.current.addCelestialBody(moon)
system.current.addVessel(iss)
system.current.celestial_bodies['Earth'].setPosition(earth_pos1)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Earth'].setTexture('pysamss/plotting/earth.jpg')
system.current.celestial_bodies['Moon'].setPosition(moon_pos1)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.celestial_bodies['Moon'].setTexture('pysamss/plotting/moon.jpg')
system.current.vessels['ISS'].setPosition([earth.radius + 404000, 0, 0], local=True)
system.current.vessels['ISS'].setVelocity([0, 7660, 0], local=True)
system.setDt(0.1)
system.setEndTime(5561.0)
system.setSaveInterval(10)
system.simulateSystem()

# Step 3: Post Processing
# Step 3.1: Load data
system.load('EarthMoonISS.psm')

# Step 3.2: Get Earth, Moon and ISS position data
timesteps = sorted(list(system.timesteps.keys()))
earthPositions = np.empty([len(timesteps), 3])
moonPositions = np.empty([len(timesteps), 3])
issPositions = np.empty([len(timesteps), 3])
for i in range(0, len(timesteps)):
    earthPositions[i,:] = system.timesteps[timesteps[i]].celestial_bodies['Earth'].getPosition()
    moonPositions[i,:] = system.timesteps[timesteps[i]].celestial_bodies['Moon'].getPosition()
    issPositions[i,:] = system.timesteps[timesteps[i]].vessels['ISS'].getPosition()
earth = system.current.celestial_bodies['Earth']
moon = system.current.celestial_bodies['Moon']
iss = system.current.vessels['ISS']

# Step 3.3: Plotting
figure = mlab.figure(size=(600, 600))

figure.scene.add_actor(earth.actor)
plotTrajectory(figure, earthPositions, (1, 1, 1))
earth.bodyRF.plot(figure, earth.getPosition(), scale_factor=earth.getRadius()*1.5)

figure.scene.add_actor(moon.actor)
plotTrajectory(figure, moonPositions, (1, 1, 1))
moon.bodyRF.plot(figure, moon.getPosition(), scale_factor=moon.getRadius()*1.5)

plotTrajectory(figure, issPositions, (1, 1, 1))
northeastdownRF = iss.getNorthEastDownRF()
northeastdownRF.plot(figure, iss.getPosition(), scale_factor=100000)

mlab.view(focalpoint=iss.getPosition(), figure=figure)

mlab.show()
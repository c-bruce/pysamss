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
earth.setPosition(earth_pos1)
earth.setVelocity(earth_vel)

# Define Moon
moon = CelestialBody('Moon', 7.348e22, 1.737e6, parent_name='Earth')
moon.setPosition(moon_pos1)
moon.setVelocity(moon_vel)

# Define ISS
stage1 = Stage(419725, 1, 10, np.array([0, 0, 0]))
iss = Vessel('ISS', [stage1], parent_name='Earth')
#iss.setPosition([earth.radius + 404000, 0, 0], local=True)
#iss.setVelocity([0, 7660, 0], local=True)

# Step 2: Setup System
system = System('EarthMoonISS')
system.currenttimestep.addCelestialBody(earth)
system.currenttimestep.addCelestialBody(moon)
system.currenttimestep.addVessel(iss)
#system.currenttimestep.setRelationships()
system.currenttimestep.vessels['ISS'].setPosition([earth.radius + 404000, 0, 0], local=True)
system.currenttimestep.vessels['ISS'].setVelocity([0, 7660, 0], local=True)
system.setDt(0.1)
system.setEndTime(5561.0)
system.setSaveInterval(10)
#system.save()
system.simulateSystem()

# Plotting
#earthPositions = np.array(earth.state)[:,3:6]
#moonPositions = np.array(moon.state)[:,3:6]
#issPositions = np.array(iss.state)[:,3:6]

figure = mlab.figure(size=(600, 600))

earthImageFile = 'pysamss/plotting/earth.jpg'
plotCelestialBody(figure, earth.getRadius(), earth.getPosition(), earthImageFile)
#plotTrajectory(figure, earthPositions, (1, 1, 1))
earth.bodyRF.plot(figure, earth.getPosition(), scale_factor=earth.radius*1.5)

moonImageFile = 'pysamss/plotting/moon.jpg'
plotCelestialBody(figure, moon.getRadius(), moon.getPosition(), moonImageFile)
#plotTrajectory(figure, moonPositions, (1, 1, 1))
moon.bodyRF.plot(figure, moon.getPosition(), scale_factor=moon.radius*1.5)

#plotTrajectory(figure, issPositions, (1, 1, 1))

northeastdownRF = iss.getNorthEastDownRF()
northeastdownRF.plot(figure, iss.getPosition(), scale_factor=100000)

mlab.view(focalpoint=iss.getPosition(), figure=figure)

mlab.show()
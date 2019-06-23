# Date: 27/01/2019
# Author: Callum Bruce
# Earth - Moon example
import numpy as np
from mayavi import mlab
from rocketsim import *
import datetime
import julian
from jplephem.spk import SPK

# Get Earth and Moon positions and velocity from jplephem
kernel = SPK.open('rocketsim/resources/de430.bsp')

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
moon = CelestialBody('Moon', 7.348e22, 1.737e6, parent=earth)
moon.setPosition(moon_pos1)
moon.setVelocity(moon_vel)
moon.setAttitude(euler2quaternion(np.rad2deg([0, 45, 0])))

# earth, moon Initial Forces
gravityForce = gravity(earth, moon)
earth.addForce(-gravityForce)
moon.addForce(gravityForce)

# Simulation loop
dt = 60
t = np.array([0])
for i in range(0,39312):
    t = np.append(t, t[i]+dt)

    # Simulate earth
    simulate(earth, euler, dt)

    # Simulate moon
    simulate(moon, euler, dt)

    # Get forces
    gravityForce = gravity(earth, moon)

    # Add forces
    earth.addForce(-gravityForce)
    moon.addForce(gravityForce)

# Plotting
earthPositions = np.array(earth.state)[:,3:6]
moonPositions = np.array(moon.state)[:,3:6]

figure = mlab.figure(size=(600, 600))

earthImageFile = 'rocketsim/plotting/earth.jpg'
plotCelestialBody(figure, earth.getRadius(), earth.getPosition(), earthImageFile)
plotTrajectory(figure, earthPositions, (1, 1, 1))
earth.bodyRF.plot(figure, earth.getPosition(), scale_factor=earth.radius*1.5)

moonImageFile = 'rocketsim/plotting/moon.jpg'
plotCelestialBody(figure, moon.getRadius(), moon.getPosition(), moonImageFile)
plotTrajectory(figure, moonPositions, (1, 1, 1))
moon.bodyRF.plot(figure, moon.getPosition(), scale_factor=moon.radius*1.5)

mlab.view(focalpoint=moon.getPosition(), figure=figure)

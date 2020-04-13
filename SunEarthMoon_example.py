# Date: 10/01/2020
# Author: Callum Bruce
# Sun - Earth - Moon Example
import numpy as np
from mayavi import mlab
from pysamss import *
import datetime
import julian
from jplephem.spk import SPK

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
sun.setPosition(sun_pos1)
sun.setVelocity(sun_vel)

# Define Earth
earth = CelestialBody('Earth', 5.972e24, 6.371e6, parent_name='Sun')
earth.setPosition(earth_pos1)
earth.setVelocity(earth_vel)

# Define Moon
moon = CelestialBody('Moon', 7.348e22, 1.737e6, parent_name='Earth')
moon.setPosition(moon_pos1)
moon.setVelocity(moon_vel)

# Setup System
system = System('SunEarthMoon')
system.addCelestialBody(sun)
system.addCelestialBody(earth)
system.addCelestialBody(moon)
system.set_dt(60.0)
system.set_endtime(31536000.0)
system.set_saveinterval(100000)
system.save()
system.simulateSystem()

# Plotting
#sunPositions = np.array(sun.state)[:,3:6]
#earthPositions = np.array(earth.state)[:,3:6]
#moonPositions = np.array(moon.state)[:,3:6]

figure = mlab.figure(size=(600, 600))

sunImageFile = 'pysamss/plotting/sun.jpg'
plotCelestialBody(figure, sun.getRadius(), sun.getPosition(), sunImageFile)
#plotTrajectory(figure, sunPositions, (1, 1, 1))
earth.bodyRF.plot(figure, earth.getPosition(), scale_factor=earth.radius*1.5)

earthImageFile = 'pysamss/plotting/earth.jpg'
plotCelestialBody(figure, earth.getRadius(), earth.getPosition(), earthImageFile)
#plotTrajectory(figure, earthPositions, (1, 1, 1))
earth.bodyRF.plot(figure, earth.getPosition(), scale_factor=earth.radius*1.5)

moonImageFile = 'pysamss/plotting/moon.jpg'
plotCelestialBody(figure, moon.getRadius(), moon.getPosition(), moonImageFile)
#plotTrajectory(figure, moonPositions, (1, 1, 1))
moon.bodyRF.plot(figure, moon.getPosition(), scale_factor=moon.radius*1.5)

mlab.view(focalpoint=moon.getPosition(), figure=figure)

mlab.show()
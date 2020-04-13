# Date: 27/01/2019
# Author: Callum Bruce
# Earth - Moon example
import numpy as np
from mayavi import mlab
from pysamss import *
import datetime
import julian
from jplephem.spk import SPK

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
moon.setAttitude(euler2quaternion(np.rad2deg([0, 45, 0])))

# Setup System
system = System('EarthMoon')
system.addCelestialBody(earth)
system.addCelestialBody(moon)
system.set_dt(60.0)
system.set_endtime(2358720.0)
system.set_saveinterval(100)
system.save()
system.simulateSystem()

# Plotting
earthPositions = np.array(earth.state)#[:,3:6]
moonPositions = np.array(moon.state)#[:,3:6]

figure = mlab.figure(size=(600, 600))

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
# Date: 25/03/2019
# Author: Callum Bruce
# Reference frames example showing parent-child get/setPosition

import numpy as np
from mayavi import mlab
from rocketsim import *

Sun = CelestialBody('Sun', 1.9885e30, 696342e3)

Earth = CelestialBody('Earth', 5.972e24, 6.371e6, parent=Sun)
Earth.setPosition([1, 0, 0], local=True)
Earth.setAttitude(euler2quaternion([np.deg2rad(45), 0, 0]))

Moon = CelestialBody('Moon', 7.348e22, 1.737e6, parent=Earth)
Moon.setPosition([0, 1, 0], local=True)
Moon.setAttitude(euler2quaternion([-np.deg2rad(45), 0, 0]), local=True)
#Moon.setPosition([0, 3.84402e8, 0], local=True)
#Moon.setVelocity([0, 10, 0], local=True)

figure = mlab.figure(size=(600, 600))

scale_factor = 1
#Sun.bodyRF.plot(figure, Sun.getPosition(), scale_factor=scale_factor)
#Earth.bodyRF.plot(figure, Earth.getPosition(), scale_factor=scale_factor)
#Moon.bodyRF.plot(figure, Moon.getPosition(), scale_factor=scale_factor)
'''
### Simulate a single second for a rotating moon and plot updated Moon.bodyRF
Moon.setAttitudeDot([0, np.deg2rad(10), 0], local=True)
simulate(Moon, euler, 1)
Moon.bodyRF.plot(figure, Moon.getPosition(), scale_factor=0.5)
'''

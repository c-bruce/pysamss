# Date: 25/03/2019
# Author: Callum Bruce
# Reference frames example showing parent-child get/setPosition

import numpy as np
from mayavi import mlab
from main import CelestialBody

Sun = CelestialBody(1.9885e30, 696342e3)
Earth = CelestialBody(5.972e24, 6.371e6, parent=Sun)
Earth.setPosition([150e9, 0, 0], local=True)
Earth.setVelocity([10, 0, 0], local=True)
Earth.rotateBodyRF(np.deg2rad(23), 0, 0)
Moon = CelestialBody(0.1, 0.1, parent=Earth)
Moon.setPosition([0, 3.84402e8, 0], local=True)
Moon.setVelocity([0, 10, 0], local=True)

figure = mlab.figure(size=(600, 600))

Sun.bodyRF.plot(figure, Sun.getPosition(), scale_factor=1e9)
Earth.bodyRF.plot(figure, Earth.getPosition(), scale_factor=1e9)
Moon.bodyRF.plot(figure, Moon.getPosition(), scale_factor=1e9)
#MoonMoon.bodyRF.plot(figure, MoonMoon.getPosition())

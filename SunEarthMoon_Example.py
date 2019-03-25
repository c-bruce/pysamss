# Date: 25/03/2019
# Author: Callum Bruce
# Reference frames example showing parent-child get/setPosition

import numpy as np
from mayavi import mlab
from main import Body

Sun = Body(1, 1)
Earth = Body(0.2, 0.2, parent=Sun)
Earth.setPosition([1, 0, 0], local=True)
Earth.setVelocity([10, 0, 0], local=True)
Moon = Body(0.1, 0.1, parent=Earth)
Moon.setPosition([0, 1, 0], local=True)
Moon.setVelocity([0, 10, 0], local=True)
MoonMoon = Body(0.1, 0.1, parent=Moon)
MoonMoon.setPosition([0, 0, 1], local=True)
MoonMoon.setVelocity([0, 0, 10], local=True)


figure = mlab.figure(size=(600, 600))

Sun.bodyRF.plot(figure, Sun.getPosition())
Earth.bodyRF.plot(figure, Earth.getPosition())
Moon.bodyRF.plot(figure, Moon.getPosition())
MoonMoon.bodyRF.plot(figure, MoonMoon.getPosition())

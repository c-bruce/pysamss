# Date: 06/01/2019
# Author: Callum Bruce
# Orbital ISS example

import numpy as np
import matplotlib.pyplot as plt
from time import time
from main import ReferenceFrame, CelestialBody, Stage, Vessel
from forcetorque import gravity, thrust
from simulate import simulate, euler

startTime = time()

# Define Earth
earth = CelestialBody(5.972e24, 6.371e6)

# Define ISS
stage1 = Stage(419725, 1, 10, [0, 0, 0])
iss = Vessel([stage1], parent=earth)
iss.setPosition([earth.radius + 404000, 0, 0])
iss.setVelocity([0, 7660, 0])

# Simulation loop
dt = 0.1
t = np.array([0])

# iss Initial Forces
gravityForce = gravity(earth, iss)
iss.addForce(gravityForce)

for i in range(0,55610):
    t = np.append(t,t[i]+dt)

    # Simulate iss
    simulate(iss, euler, dt)

    # Calculate forces and torques acting on iss
    gravityForce = gravity(earth, iss)
    iss.addForce(gravityForce)

# Plotting
state = np.array(iss.state)
issPos = state[:,3:6]
fig, ax = plt.subplots()
ax.axis('equal')
ax.axis([-earth.radius*2,earth.radius*2,-earth.radius*2,earth.radius*2])
earthPosition = earth.getPosition()
earthPlot = plt.Circle((earthPosition[0], earthPosition[1]),earth.radius,color='b')
ax.add_artist(earthPlot)
ax.plot(state[0:,3],state[0:,4],color='k',lw=0.5)
plt.show()

endTime = time()
print(str(endTime - startTime) + ' Seconds')

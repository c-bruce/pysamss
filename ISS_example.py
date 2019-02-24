# Date: 06/01/2019
# Author: Callum Bruce
# Orbital ISS example

import numpy as np
import matplotlib.pyplot as plt
from time import time
from main import ReferenceFrame, Body, Stage, Vehicle
from forcetorque import gravity, thrust
from simulate import simulate, euler

startTime = time()

# Define Earth
earthRF = ReferenceFrame()
earth = Body(5.972e24,6.371e6,[0,0,0,0,0,0],earthRF)

# Define ISS
issRF = ReferenceFrame()
stage1 = Stage(419725,1,10,[0,0])
iss = Vehicle([stage1],[0,7660,earth.radius+404000,0,0,0],earthRF,issRF)

# Simulation loop
dt = 0.1
t = np.array([0])

# iss Initial Forces
forceGravity = gravity(earth,iss)
iss.appendU(list(np.append(forceGravity,0)))

for i in range(0,55610):
    t = np.append(t,t[i]+dt)

    # Simulate iss
    simulate(iss,issRF,euler,dt)

    # Calculate forces and torques acting on iss
    forceGravity = gravity(earth,iss)
    iss.appendU(list(np.append(forceGravity,0)))

# Plotting
state = np.array(iss.state)
issPos = iss.getPosition()
fig, ax = plt.subplots()
ax.axis('equal')
ax.axis([-earth.radius*2,earth.radius*2,-earth.radius*2,earth.radius*2])
earthPosition = earth.getPosition()
earthPlot = plt.Circle((earthPosition[0], earthPosition[1]),earth.radius,color='b')
ax.add_artist(earthPlot)
ax.plot(state[0:,2],state[0:,3],color='k',lw=0.5)
ax.plot([issPos[0],issPos[0]+issRF.i[0]*1000000],[issPos[1],issPos[1]+issRF.i[1]*1000000],c='r')
ax.plot([issPos[0],issPos[0]+issRF.j[0]*1000000],[issPos[1],issPos[1]+issRF.j[1]*1000000],c='g')
plt.show()

endTime = time()
print(str(endTime - startTime) + ' Seconds')

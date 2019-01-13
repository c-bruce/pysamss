# Date: 06/01/2019
# Author: Callum Bruce
# Script for modelling launch vehicle system
import numpy as np
import matplotlib.pyplot as plt
from time import time
from main import referenceFrame, body, stage, vehicle
from forcetorque import gravity, thrust
from simulate import simulate, euler

startTime = time()

# Define Earth
earthRF = referenceFrame()
earth = body(5.972e24,6.371e6,[0,0],earthRF)

# Define ISS
issRF = referenceFrame()
stage1 = stage(419725,1,10,[0,0])
iss = vehicle([stage1],[0,7660,earth.radius+404000,0,0,0],earthRF,issRF)

# Simulation loop
state = np.array([iss.getState()])
us = np.array([np.append(gravity(earth,iss),0)])

dt = 0.1
for i in range(0,55610):
    state1 = simulate(iss,issRF,euler,us[i],dt) # Calculate state1
    iss.setState(state1) # Set iss state = state1
    state = np.append(state,[state1],axis=0) # Append state1 to state for plotting later
    us = np.append(us,[np.append(gravity(earth,iss),0)],axis=0) # Append new u to us

# Plotting
issPos = iss.getPosition()
fig, ax = plt.subplots()
ax.axis('equal')
ax.axis([-earth.radius*2,earth.radius*2,-earth.radius*2,earth.radius*2])
earthPlot = plt.Circle((earth.position[0],earth.position[1]),earth.radius,color='b')
ax.add_artist(earthPlot)
ax.plot(state[0:,2],state[0:,3],color='k',lw=0.5)
ax.plot([issPos[0],issPos[0]+issRF.i[0]*1000000],[issPos[1],issPos[1]+issRF.i[1]*1000000],c='r')
ax.plot([issPos[0],issPos[0]+issRF.j[0]*1000000],[issPos[1],issPos[1]+issRF.j[1]*1000000],c='g')

endTime = time()
print(str(endTime - startTime) + ' seconds')
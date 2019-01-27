# Date: 27/01/2019
# Author: Callum Bruce
# Earth - Moon example

import numpy as np
import matplotlib.pyplot as plt
from time import time
from main import referenceFrame, body, stage, vehicle
from forcetorque import gravity, thrust
from simulate import simulate, euler

startTime = time()

# Define Earth
earthRF = referenceFrame()
earth = body(5.972e24,6.371e6,[0,0,0,0,0,0],earthRF)
state_earth = np.array([earth.getState()])

# Define Moon
moonRF = referenceFrame()
moon = body(7.348e22,1.737e6,[0,1022,3.84402e8,0,0,0],moonRF)
state_moon = np.array([moon.getState()])

# Initial us_earth, us_moon
gravityForce = gravity(earth,moon)
us_earth = np.array([np.append(-gravityForce,0)])
us_moon = np.array([np.append(gravityForce,0)])

# Simulation loop
dt = 60
for i in range(0,39312):
    state_earth1 = simulate(earth,earthRF,euler,us_earth[i],dt) # Calculate state_earth1
    earth.setState(state_earth1) # Set earth state = state_earth1
    state_earth = np.append(state_earth,[state_earth1],axis=0) # Append state_earth1 to state_earth for plotting later
    
    state_moon1 = simulate(moon,moonRF,euler,us_moon[i],dt) # Calculate state_moon1
    moon.setState(state_moon1) # Set moon state = state_moon1
    state_moon = np.append(state_moon,[state_moon1],axis=0) # Append state_moon1 to state_moon for plotting later
    
    gravityForce = gravity(earth,moon)
    us_earth = np.append(us_earth,[np.append(-gravityForce,0)],axis=0) # Append new u_earth to us_earth
    us_moon = np.append(us_moon,[np.append(gravityForce,0)],axis=0) # Append new u_moon to us_moon

# Plotting
fig, ax = plt.subplots()
ax.axis('equal')
ax.axis([-earth.radius*100,earth.radius*100,-earth.radius*100,earth.radius*100])

earthPosition = earth.getPosition()
earthPlot = plt.Circle((earthPosition[0], earthPosition[1]),earth.radius,color='b')
ax.add_artist(earthPlot)
ax.plot(state_moon[0:,2],state_moon[0:,3],color='k',lw=0.5)

moonPosition = moon.getPosition()
moonPlot = plt.Circle((moonPosition[0], moonPosition[1]),moon.radius,color='gray')
ax.add_artist(moonPlot)
ax.plot(state_moon[0:,2],state_moon[0:,3],color='k',lw=0.5)
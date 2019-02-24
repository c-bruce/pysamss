# Date: 27/01/2019
# Author: Callum Bruce
# Earth - Moon example

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

# Define Moon
moonRF = ReferenceFrame()
moon = Body(7.348e22,1.737e6,[0,1022,3.84402e8,0,0,0],moonRF)

# earth, moon Initial Forces
gravityForce = gravity(earth,moon)
earth.appendU(list(np.append(-gravityForce,0)))
moon.appendU(list(np.append(gravityForce,0)))

# Simulation loop
dt = 60
t = np.array([0])
for i in range(0,39312):
    t = np.append(t,t[i]+dt)

    # Simulate earth
    simulate(earth,earthRF,euler,dt)

    # Simulate moon
    simulate(moon,moonRF,euler,dt)

    # Get forces
    gravityForce = gravity(earth,moon)

    # Store force
    earth.appendU(list(np.append(-gravityForce,0)))
    moon.appendU(list(np.append(gravityForce,0)))

# Plotting
state_earth = np.array(earth.state)
state_moon = np.array(moon.state)
fig, ax = plt.subplots()
ax.axis('equal')
ax.axis([-earth.radius*100,earth.radius*100,-earth.radius*100,earth.radius*100])

earthPosition = earth.getPosition()
earthPlot = plt.Circle((earthPosition[0], earthPosition[1]),earth.radius,color='b')
ax.add_artist(earthPlot)
ax.plot(state_earth[0:,2],state_earth[0:,3],color='k',lw=0.5)

moonPosition = moon.getPosition()
moonPlot = plt.Circle((moonPosition[0], moonPosition[1]),moon.radius,color='gray')
ax.add_artist(moonPlot)
ax.plot(state_moon[0:,2],state_moon[0:,3],color='k',lw=0.5)
plt.show()

endTime = time()
print(str(endTime - startTime) + ' Seconds')

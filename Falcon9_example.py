# Date: 06/01/2019
# Author: Callum Bruce
# Suborbital Falcon9 example

import numpy as np
import matplotlib.pyplot as plt
from time import time
from main import referenceFrame, body, stage, vehicle
from forcetorque import gravity, thrust
from simulate import simulate, euler
from control import PIDcontroller

startTime = time()

# Define Earth
earthRF = referenceFrame()
earth = body(5.972e24,6.371e6,[0,0,0,0,0,0],earthRF)

# Define Falcon9
falcon9RF = referenceFrame()
stage1 = stage(258500,1.85,13.1,[-6.55,0])
stage2 = stage(52000,1.85,35,[-30.6,0])
falcon9 = vehicle([stage1,stage2],[0,0,earth.radius+48.1,0,0,0],earthRF,falcon9RF)
Isp = 300 # (s)
m_dot = 1500 # (kg/s)

# Define controller
gains = [0.12,0.01,0.35]
lims = [5,-5]
windup = 0.2
yawControl = PIDcontroller(gains,lims,windup)
d = np.array([0.0]) # Initial gimbal angle (deg)

# Simulation loop
dt = 0.1
t = np.array([0])
forceGravity = np.array(gravity(earth,falcon9)) # forceGravity
forceThrust, torqueThrust = thrust(earth,falcon9,m_dot,Isp,d[-1],dt) # forceThrust, torqueThrust from fuel burn
forceThrustSave = np.array([forceThrust])
us = np.array([np.append(forceGravity+forceThrust,torqueThrust)]) # [Fx, Fy, Mz] earthRF

for i in range(0,8000):
    t = np.append(t,t[i]+dt)

    # Simulate falcon9
    simulate(falcon9,falcon9RF,euler,us[i],dt)
    '''
    # Fix attitude
    if i > 300 and i < 900:
        att = np.deg2rad(20)
        falcon9.setPhi(att)
    elif i > 900:
        v = falcon9.getVelocity()
        att = np.arctan(v[1]/v[0])
        falcon9.setPhi(att)
        print(np.rad2deg(att))
    '''
    # Use PID to control phi
    if i > 300 and i < 900: # Control phi = 20 deg
        phi_pv = falcon9.getPhi()
        phi_sp = np.deg2rad(20)
        d_new = yawControl.calculate_output(phi_pv,phi_sp,dt)
        d = np.append(d,d_new)
    elif i > 900: # Control phi = velocity vector
        v = falcon9.getVelocity()
        phi_pv = falcon9.getPhi()
        phi_sp = np.abs(np.arctan(v[1]/v[0]))
        d_new = yawControl.calculate_output(phi_pv,phi_sp,dt)
        d = np.append(d,d_new)
    else:
        d = np.append(d,0)

    # Calculate forces and torques acting on falcon9
    forceGravity = np.array(gravity(earth,falcon9)) # forceGravity
    forceThrust, torqueThrust = thrust(earth,falcon9,m_dot,Isp,d[-1],dt) # forceThrust, torqueThrust from fuel burn
    forceThrustSave = np.append(forceThrustSave,[forceThrust],axis=0)
    u = np.array([np.append(forceGravity+forceThrust,torqueThrust)]) # [Fx, Fy, Mz] earthRF
    us = np.append(us,u,axis=0) # Append new u to us

# Plotting
state = falcon9.state
falcon9Pos = falcon9.getPosition()
fig, ax = plt.subplots()
ax.axis('equal')
ax.axis([-earth.radius*2,earth.radius*2,-earth.radius*2,earth.radius*2])
earthPosition = earth.getPosition()
earthPlot = plt.Circle((earthPosition[0], earthPosition[1]),earth.radius,color='b')
ax.add_artist(earthPlot)
ax.plot(state[0:,2],state[0:,3],color='k',lw=0.5)
ax.plot([falcon9Pos[0],falcon9Pos[0]+falcon9RF.i[0]*1000000],[falcon9Pos[1],falcon9Pos[1]+falcon9RF.i[1]*1000000],c='r')
ax.plot([falcon9Pos[0],falcon9Pos[0]+falcon9RF.j[0]*1000000],[falcon9Pos[1],falcon9Pos[1]+falcon9RF.j[1]*1000000],c='g')

# Plot state over time [d, phi, phi_dot]
fig, ax1 = plt.subplots(3,1)
ax1[0].plot(t,d)
ax1[0].set_title('d')
ax1[0].set_ylabel('[rad]')
ax1[0].grid()
ax1[1].plot(t,state[0:,5])
ax1[1].set_title('phi')
ax1[1].set_ylabel('[rad]')
ax1[1].grid()
ax1[2].plot(t,state[0:,4])
ax1[2].set_title('phi_dot')
ax1[2].set_ylabel('[rad/s]')
ax1[2].grid()

# Plot controller [phi_SP phi_PV, error, int_error]
fig, ax2 = plt.subplots(3,1)
ax2[0].plot(yawControl.SP)
ax2[0].plot(yawControl.PV)
ax2[0].set_title('phi')
ax2[0].set_ylabel('[rad]')
ax2[0].legend(['Set Point','State'])
ax2[0].grid()
ax2[1].plot(yawControl.error)
ax2[1].set_title('error')
ax2[1].set_ylabel('[rad]')
ax2[1].grid()
ax2[2].plot(yawControl.int)
ax2[2].set_title('int_error')
ax2[2].set_ylabel('[rad]')
ax2[2].grid()
plt.show()

endTime = time()
print(str(endTime - startTime) + ' Seconds')

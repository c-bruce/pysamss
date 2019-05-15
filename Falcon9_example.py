# Date: 16/04/2019
# Author: Callum Bruce
# Suborbital Falcon9 example
import numpy as np
from mayavi import mlab
from pyquaternion import Quaternion
from rocketsim import *

# Define Earth
earth = CelestialBody(5.972e24, 6.371e6)

# Define Falcon9
stage1 = Stage(258500, 1.85, 35, [-30.6, 0, 0])
stage2 = Stage(52000, 1.85, 13.1, [-6.55, 0, 0])
falcon9 = Vessel([stage1, stage2], parent=earth)
falcon9.setPosition([earth.radius + 48.1, 0, 0])
falcon9.updateNorthEastDownRF()
falcon9.initAttitude()
# Plotting
figure = mlab.figure(size=(600, 600))

earthImageFile = 'plotting/earth.jpg'
#plotCelestialBody(figure, earth.getRadius(), earth.getPosition(), earthImageFile)

#falcon9.updateNorthEastDownRF()
falcon9.northeastdownRF.plot(figure, falcon9.getPosition(), scale_factor=100000)

### Setup Initial bodyRF position ###
#falcon9.initAttitude()
#falcon9.bodyRF.plot(figure, falcon9.getPosition(), scale_factor=200000)

falcon9.addTorque([531343.125 * np.deg2rad(0), 6.01303303e+07 * np.deg2rad(0), 6.01303303e+07 * np.deg2rad(175)])
#falcon9.addTorque([531343.125 * np.deg2rad(95), 6.01303303e+07 * np.deg2rad(160), 6.01303303e+07 * np.deg2rad(-50)])
#falcon9.addForce([310500 * 100, 0, 0], local=True)
simulate(falcon9, euler, 1)
dt = 0.001
for i in range(0,1000):
    simulate(falcon9, euler, dt)
falcon9.bodyRF.plot(figure, falcon9.getPosition(), scale_factor=200000)

mlab.view(focalpoint=falcon9.getPosition(), figure=figure)

figure1 = mlab.figure(size=(600, 600))
universalAttitude = falcon9.getAttitude()
universalAttitudeRF = ReferenceFrame()
universalAttitudeRF.plot(figure1, [0, 0, 0])
universalAttitudeRF_new = ReferenceFrame()
universalAttitudeRF_new.rotate(universalAttitude)
universalAttitudeRF_new.plot(figure1, [0, 0, 0], scale_factor=2)

figure2 = mlab.figure(size=(600, 600))
localAttitude = falcon9.getAttitude(local=True)
localAttitudeRF = ReferenceFrame()
localAttitudeRF.plot(figure2, [0, 0, 0])
localAttitudeRF_new = ReferenceFrame()
localAttitudeRF_new.rotate(localAttitude)
localAttitudeRF_new.plot(figure2, [0, 0, 0], scale_factor=2)

### Gimbal Control: ###
# Step 1: Work out the torque vector required to turn onto a heading.
# Step 2: Find unit_res (at CoT) in bodyRF equivelant to apply torque in direction of torque vector.
# Step 3: Find gimbal angle to achieve unit_res.
# Step 4: Based on Kp, Ki and Kd turn onto heading.
'''
Isp = 300 # (s)
m_dot = 1500 # (kg/s)

# Define controller
gains = [0.12, 0.01, 0.35]
lims = [5, -5]
windup = 0.2
yawControl = PIDcontroller(gains, lims, windup)
d = np.array([0.0]) # Initial gimbal angle (deg)

# Simulation loop
dt = 0.1
t = np.array([0])

# falcon9 Initial Forces
forceGravity = gravity(earth,falcon9) # forceGravity
forceThrust, torqueThrust = thrust(earth,falcon9,m_dot,Isp,d[-1],dt) # forceThrust, torqueThrust from fuel burn
forceThrustSave = np.array([forceThrust])
falcon9.appendU(list(np.append(forceGravity+forceThrust,torqueThrust)))

for i in range(0,8000):
    t = np.append(t,t[i]+dt)

    # Simulate falcon9
    simulate(falcon9,falcon9RF,euler,dt)

    # Fix attitude
    if i > 300 and i < 900:
        att = np.deg2rad(20)
        falcon9.setPhi(att)
    elif i > 900:
        v = falcon9.getVelocity()
        att = np.arctan(v[1]/v[0])
        falcon9.setPhi(att)
        print(np.rad2deg(att))

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
    forceGravity = gravity(earth,falcon9) # forceGravity
    forceThrust, torqueThrust = thrust(earth,falcon9,m_dot,Isp,d[-1],dt) # forceThrust, torqueThrust from fuel burn
    forceThrustSave = np.append(forceThrustSave,[forceThrust],axis=0)
    falcon9.appendU(list(np.append(forceGravity+forceThrust,torqueThrust)))
'''

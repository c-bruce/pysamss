# Date: 16/04/2019
# Author: Callum Bruce
# Suborbital Falcon9 example

import numpy as np
from mayavi import mlab
from main import ReferenceFrame, CelestialBody, Stage, Vessel
from forcetorque import gravity, thrust
from simulate import simulate, euler
from plotting import plotCelestialBody, plotTrajectory
from helpermath import *
from pyquaternion import Quaternion

# Define Earth
earth = CelestialBody(5.972e24, 6.371e6)

# Define Falcon9
stage1 = Stage(258500, 1.85, 35, [-30.6, 0, 0])
stage2 = Stage(52000, 1.85, 13.1, [-6.55, 0, 0])
falcon9 = Vessel([stage1, stage2], parent=earth)
falcon9.setPosition([earth.radius + 48.1, 0, 0])

# Plotting
figure = mlab.figure(size=(600, 600))

earthImageFile = 'plotting/earth.jpg'
#plotCelestialBody(figure, earth.getRadius(), earth.getPosition(), earthImageFile)

falcon9.updateNorthEastDownRF()
falcon9.northeastdownRF.plot(figure, falcon9.getPosition(), scale_factor=100000)

### Setup Initial bodyRF position ###
falcon9.initAttitude()
#falcon9.bodyRF.plot(figure, falcon9.getPosition(), scale_factor=200000)

falcon9.addTorque([0, 6.01303303e+07 * np.deg2rad(160), 0])
#falcon9.addForce([310500 * 100, 0, 0], local=True)
simulate(falcon9, euler, 1)
dt = 0.01
for i in range(0,100):
    simulate(falcon9, euler, dt)
falcon9.bodyRF.plot(figure, falcon9.getPosition(), scale_factor=200000)

mlab.view(focalpoint=falcon9.getPosition(), figure=figure)
'''
# Get bodyi in northeastdownRF
R = referenceFrames2rotationMatrix(falcon9.universalRF, falcon9.northeastdownRF)
print(np.dot(R, falcon9.bodyRF.i))

# Get heading and convert to vector in northeastdownRF
heading = falcon9.getHeading()
vector = heading2vector(heading)
print(vector)
'''
# Checking getAttitude(local=True) works correctly
#R = referenceFrames2rotationMatrix(self.universalRF, self.parentRF) # Transform from universalRF to parentRF
#position = np.dot(R, self.getPosition() - self.parent.getPosition())
R1 = referenceFrames2rotationMatrix(falcon9.bodyRF, falcon9.universalRF)
q1 = Quaternion(matrix=R1)
print(np.rad2deg(quaternion2euler(q1)))
R2 = referenceFrames2rotationMatrix(falcon9.northeastdownRF, falcon9.universalRF)
q2 = Quaternion(matrix=R2)
print(np.rad2deg(quaternion2euler(q2)))
R3 = referenceFrames2rotationMatrix(falcon9.bodyRF, falcon9.northeastdownRF)
q3 = Quaternion(matrix=R3)
print(np.rad2deg(quaternion2euler(q3)))
attitude = falcon9.getAttitude()
print(np.rad2deg(quaternion2euler(attitude)))

q4 = euler2quaternion(np.deg2rad([0, 0, 90]))
print(np.rad2deg(quaternion2euler(q4)))
q5 = euler2quaternion(np.deg2rad([0, 90, 0]))
print(np.rad2deg(quaternion2euler(q5)))
q6 = q5 * q4 # q6 does the correct rotation at initAttitude
print(np.rad2deg(quaternion2euler(q6)))
q7 = q3 + Quaternion(0, 0, 0, 1)
print(np.rad2deg(quaternion2euler(q7)))
q8 = q2.inverse * q2.rotate(attitude) # q6 does the correct rotation
print(np.rad2deg(quaternion2euler(q8)))
q9 = q2.inverse.rotate(q8)
print(np.rad2deg(quaternion2euler(q9)))

falcon9.northeastdownRF.rotate(q8)
falcon9.northeastdownRF.plot(figure, falcon9.getPosition(), scale_factor=50000)
'''
northeastdownRF_NED = ReferenceFrame()
bodyRF_NED = ReferenceFrame()
bodyRF_NED.rotate(q3)
R = referenceFrames2rotationMatrix(northeastdownRF_NED, bodyRF_NED)
attitude_local = Quaternion(matrix=R)
print(np.rad2deg(quaternion2euler(attitude_local)))
q = q2.rotate(q3)

'''
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

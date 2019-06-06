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
falcon9.setPosition([earth.radius, 0, 0])
falcon9.updateNorthEastDownRF()
falcon9.initAttitude()

Isp = 300 # (s)
m_dot = 1500 # (kg/s)

# Define controller
gains = [0.12, 0.01, 0.35]
lims = [5, -5]
windup = 0.2
pitchControl = PIDcontroller(gains, lims, windup)
d_theta = 0.0 # Initial gimbal angle theta (rad)
d_psi = 0.0 # Initial gimbal angle psi (rad)
gimbal = [[d_theta, d_psi]]

# Simulation loop
dt = 0.1
t = [0]

# falcon9 Initial Forces
# Gravity:
forceGravity = gravity(earth, falcon9)
falcon9.addForce(forceGravity)
# Thrust:
forceThrust, torqueThrust = thrust(falcon9, m_dot, Isp, gimbal[-1], dt)
falcon9.addForce(forceThrust, local=True)
falcon9.addTorque(torqueThrust)
forceThrustSave = [forceThrust.tolist()]
torqueThrustSave = [torqueThrust.tolist()]

for i in range(0, 8000):
    t.append(t[i] + dt)

    # Simulate falcon9
    simulate(falcon9, euler, dt)
    # Use PID to control phi
    if i > 300 and i < 900: # Control pitch = 70 deg
        pitch_pv = falcon9.getHeading()[1]
        pitch_sp = np.deg2rad(70)
        d_theta = pitchControl.calculate_output(pitch_pv, pitch_sp, dt)
        d_psi = 0
        gimbal.append([d_theta, d_psi])
    elif i > 900 and i < 1500:
        pitch_pv = falcon9.getHeading()[1]
        pitch_sp = np.deg2rad(45)
        d_theta = pitchControl.calculate_output(pitch_pv, pitch_sp, dt)
        d_psi = 0
        gimbal.append([d_theta, d_psi])
    elif i > 1500: # Control pitch = velocity vector
        v = falcon9.getVelocity()
        pitch_pv = falcon9.getHeading()[1]
        pitch_sp = np.abs(np.arctan(v[0] / v[1]))
        d_theta = pitchControl.calculate_output(pitch_pv, pitch_sp, dt)
        d_psi = 0
        gimbal.append([d_theta, d_psi])
    else:
        d_theta = 0
        d_psi = 0
        gimbal.append([d_theta, d_psi])

    # Calculate forces and torques acting on falcon9
    # Gravity:
    forceGravity = gravity(earth, falcon9)
    falcon9.addForce(forceGravity)
    # Thrust:
    forceThrust, torqueThrust = thrust(falcon9, m_dot, Isp, gimbal[-1], dt)
    falcon9.addForce(forceThrust, local=True)
    falcon9.addTorque(torqueThrust)
    forceThrustSave.append(forceThrust.tolist())
    torqueThrustSave.append(torqueThrust.tolist())

# Plotting
falcon9Positions = np.array(falcon9.state)[:,3:6]

figure = mlab.figure(size=(600, 600))

earthImageFile = 'rocketsim/plotting/earth.jpg'
plotCelestialBody(figure, earth.getRadius(), earth.getPosition(), earthImageFile)
plotTrajectory(figure, falcon9Positions, (1, 1, 1))
falcon9.bodyRF.plot(figure, falcon9.getPosition(), scale_factor=1000)

mlab.view(focalpoint=falcon9.getPosition(), figure=figure)

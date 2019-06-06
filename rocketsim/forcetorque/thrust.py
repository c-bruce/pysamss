# Date: 06/01/2019
# Author: Callum Bruce
# Calculate force and torque due thrust
import numpy as np
from ..helpermath.helpermath import *

def thrust(vessel, m_dot, Isp, gimbal, dt):
    """
    Calculate bodyRF forceThrust and torqueThrust due to fuel burn acting on vehicle.

    Args:
        vessel (obj): Vessel object (i.e. falcon9)
        m_dot (float): Mass of fuel burnt (kg)
        Isp (float): Specific impulse (s)
        gimbal (list): Gimbal angle [theta, psi] (rad)
        dt (float): Time step

    Returns:
        forceThrust (np.array): np.array force acting on CoM in bodyRF due to thrust
        torqueThrust (np.array): np.array torque acting about CoM in bodyRF due to thrust
    """
    if vessel.stages[0].wetmass > 0: # If stage has fuel calculate forceThrust and torqueThrust
        # Gimbal angles
        d_theta = gimbal[0]
        d_psi = gimbal[1]
        # Calculate thrust magnitude
        g0 = 9.81 # Standard gravity (m/s^2)
        thrust = g0 * Isp * m_dot
        # Calculate forceThrust vector
        forceThrust = np.array([thrust * np.cos(d_psi) * np.cos(d_theta),
                                thrust * np.sin(d_psi),
                                thrust * np.sin(d_theta)])
        # Calculate torqueThrust vector
        momentArm = vessel.CoM - vessel.CoT
        torqueThrust = np.cross(momentArm, forceThrust)
        # Update vehicle mass due to fuel burn
        vessel.updateMass(-m_dot * dt)
    else: # If stage has zero fuel forceThrust and torqueThrust = [0, 0, 0]
        forceThrust = np.array([0, 0, 0])
        torqueThrust = np.array([0, 0, 0])
    return forceThrust, torqueThrust

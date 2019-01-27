# Date: 06/01/2019
# Author: Callum Bruce
# Calculate forces and torques acting on objects

import numpy as np
from helpermath import transformationMatrix

def gravity(obj1,obj2):
    """
    Calculate gravityForce acting on an obj2 (body or vehicle.
    
    Args:
        obj1 (obj): Body or vehicle object
        obj2 (obj): Body or vehicle object
    
    Returns:
        gravityForce (np.array): gravityForce acting on obj2.
    """
    G = 6.67408e-11 # Gravitational constant [m**3.kg**-1.s**-2]
    obj1Mass = obj1.getMass()
    obj2Mass = obj2.getMass()
    obj1Position = obj1.getPosition()
    obj2Position = obj2.getPosition()
    r = np.linalg.norm(obj1Position - obj2Position)
    F = G * ((obj1Mass * obj2Mass) / r**2)
    gravityForce = F * (obj1Position - obj2Position) / np.linalg.norm(obj1Position - obj2Position)
    return gravityForce

def thrust(body,vehicle,m_dot,Isp,d,dt):
    """
    Calculate bodyRF forceThrust and torqueThrust due to fuel burn acting on vehicle.
    
    Args:
        body (obj): Body object (i.e. earth)
        vehicle (obj): Vehicle object (i.e. falcon9)
        m_dot (float): Mass of fuel burnt (kg)
        Isp (float): Specific impulse (s)
        d (float): Gimbal angle (deg)
        dt (float): Time step
    
    Returns:
        forceThrust (np.array): np.array force acting on CoM in bodyRF due to thrust
        torqueThrust (np.array): np.array torque acting about CoM in bodyRF due to thrust
    """
    if vehicle.stages[0].wetmass > 0: # If stage has zero fuel forceThrust and torqueThrust = 0
        # Calculate thrust magnitude
        g0 = 9.81 # Standard gravity (m/s^2)
        thrust = g0 * Isp * m_dot
        
        # Calculate bodyRF torque vector acting @ CoM
        momentArm = vehicle.CoM - vehicle.CoT
        forceCoT = thrust*np.array([np.cos(d),np.sin(d)]) # vehicleRF forces acting @ CoT
        torqueThrust = np.cross(momentArm,forceCoT) # Torque = r x F (1x1 for 2D case therefore no transform needed)

        # Calculate bodyRF force vector acting @ CoM
        forceThrust_body = thrust*np.array([np.cos(d),0]) # vehicleRF forces acting @ CoM
        referenceFrame1 = vehicle.getRF()
        referenceFrame2 = body.getRF()
        T = transformationMatrix(referenceFrame1,referenceFrame2) # transformationMatrix vehicleRF -> bodyRF
        forceThrust = np.dot(T,forceThrust_body) # bodyRF forces acting @ CoM
        
        # Update vehicle mass due to fuel burn
        vehicle.updateMass(-m_dot*dt)
    else:
        torqueThrust = np.array(0)
        forceThrust = np.array([0,0])
    return forceThrust, torqueThrust
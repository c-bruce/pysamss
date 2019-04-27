# Date: 06/01/2019
# Author: Callum Bruce
# State space simulator and integration schemes module

import numpy as np
from pyquaternion import Quaternion

def simulate(obj, scheme, dt):
    """
    Simulate body/vehicle using a given integration scheme.

    Args:
        obj (object): Object to simulate (body or vehicle).
        scheme (function): Integration scheme i.e. euler.
        dt (float): Time step.

    Returns:
        state1 (list): Updated state vector.

    Notes:
        state_d = [u_d, v_d, w_d, x_d, y_d, z_d, phi_dd, theta_dd, psi_dd, phi_d, theta_d, psi_d].
        state = [u, v, w, x, y, z, phi_d, theta_d, psi_d, phi, theta, psi].
        U = [Fx, Fy, Fz, Mx, My, Mz].
    """
    state0 = obj.getState()
    U = obj.getU()
    m = obj.getMass()
    I = obj.getI()
    Ii = np.linalg.inv(I) # I**-1

    A = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # . [u, v, w, x, y, z, phi_d, theta_d, psi_d, w, x, y, z]
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -0.5 * state0[6], -0.5 * state0[7], -0.5 * state0[8]],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5 * state0[6], 0, 0.5 * state0[8], -0.5 * state0[7]],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5 * state0[7], -0.5 * state0[8], 0, 0.5 * state0[6]],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5 * state0[8], 0.5 * state0[7], -0.5 * state0[6], 0]])

    B = np.array([[1/m, 0, 0, 0, 0, 0], # . [Fx, Fy, Fz, Mx, My, Mz]
                  [0, 1/m, 0, 0, 0, 0],
                  [0, 0, 1/m, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, Ii[0,0], Ii[0,1], Ii[0,2]],
                  [0, 0, 0, Ii[1,0], Ii[1,1], Ii[1,2]],
                  [0, 0, 0, Ii[2,0], Ii[2,1], Ii[2,2]],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0]])

    state_d = np.dot(A, state0) + np.dot(B, U)

    state1 = scheme(state0, state_d, dt)
    obj.appendState(state1.tolist())
    obj.appendU([0, 0, 0, 0, 0, 0])
    obj.bodyRF.rotateAbs(Quaternion(state1[9:]))
    if type(obj) is Vessel:
        obj.updateNorthEastDownRF()

# Integration schemes
def euler(state0, state_d, dt):
    """
    Perform Euler integration.

    Args:
        state0 (list): Objects initial state vector [u, v, w, x, y, z, phi_d, theta_d, psi_d, phi, theta, psi].
        state_d (list): Objects state derivative vector [u_d, v_d, w_d, x_d, y_d, z_d, phi_dd, theta_dd, psi_dd, phi_d, theta_d, psi_d].
        dt (float): Timestep (s).

    Returns:
        state1 (list): Updated state vector after time dt [u, v, w, x, y, z, phi_d, theta_d, psi_d, phi, theta, psi].
    """
    state1 = state0 + state_d * dt
    return state1

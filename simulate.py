# Date: 06/01/2019
# Author: Callum Bruce
# State space simulator and integration schemes module

import numpy as np

def simulate(obj,objRF,scheme,dt):
    """
    Simulate body/vehicle using a given integration scheme.

    Args:
        obj (object): Object to simulate (body or vehicle)
        objRF (object): Reference frame object belonging to obj
        scheme (function): Integration scheme {euler}
        dt (float): Time step

    Returns:
        state1 (list): Updated state vector

    Notes:
        state_dot = [u_d, v_d, w_d, x_d, y_d, z_d, phi_dd, theta_dd, psi_dd, phi_d, theta_d, psi_d]
        state = [u, v, w, x, y, z, phi_d, theta_d, psi_d, phi, theta, psi]
        U = [Fx, Fy, Fz, Mx, My, Mz]
    """
    state0 = obj.getState()
    U = obj.getU()
    m = obj.getMass()
    Ix = obj.getIx()
    Iy = obj.getIy()
    Iz = obj.getIz()

    A = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # . [u, v, w, x, y, z, phi_d, theta_d, psi_d, phi, theta, psi]
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]])

    B = np.array([[1/m, 0, 0, 0, 0, 0], # . [Fx, Fy, Fz, Mx, My, Mz]
                  [0, 1/m, 0, 0, 0, 0],
                  [0, 0, 1/m, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 1/Ix, 0, 0],
                  [0, 0, 0, 0, 1/Iy, 0],
                  [0, 0, 0, 0, 0, 1/Iz],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0]])

    state_dot = np.dot(A,state0) + np.dot(B,U)

    state1 = scheme(state0,state_dot,dt)
    obj.appendState(state1)
    objRF.rotate(state1[5])
    obj.setRF(objRF)

# Integration schemes
def euler(state0,state_dot,dt):
    state1 = state0 + state_dot*dt
    return state1

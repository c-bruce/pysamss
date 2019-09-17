# Date: 06/01/2019
# Author: Callum Bruce
# Integration schemes
import numpy as np

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

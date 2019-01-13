import numpy as np

def simulate(obj,objRF,scheme,u,dt):
    """
    Simulate the vehicle using a given integration scheme.
    
    Args:
        scheme (function): Integration scheme {euler}
        u (list): Input vector
        dt (float): Time step
    
    Returns:
        state1 (list): Updated state vector
    """
    state0 = obj.getState()
    m = obj.getMass()
    Iz = obj.getIz()
    
    A = np.array([[0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [1, 0, 0, 0, 0, 0],
                  [0, 1, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 1, 0]])
    
    B = np.array([[1/m, 0, 0],
                  [0, 1/m, 0],
                  [0, 0, 0],
                  [0, 0, 0],
                  [0, 0, 1/Iz],
                  [0, 0, 0]])
    
    state_dot = np.dot(A,state0) + np.dot(B,u)
    
    state1 = scheme(state0,state_dot,dt)
    objRF.rotate(state1[5])
    #objRF.rotateDot(state1[4])
    obj.setRF(objRF)
    return state1

# Integration schemes
def euler(state0,state_dot,dt):
    state1 = state0 + state_dot*dt
    return state1
# pySAMSS

Python Space Asset Management and Simulation System

A Python package for managing and simulating assets in Space.

pySAMSS provides a full 6 degree of freedom state space model representation of CelestialBody and Vessel objects. Using numerical integration the future state of CelestialBody and Vessel objects can be found explicitly where:

```python
state0 = np.array([u, v, w, x, y, z, phi_d, theta_d, psi_d, qw, qx, qy, qz]) # State vector

U = np.array([Fx, Fy, Fz, Mx, My, Mz]) # Input vector

A = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
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
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5 * state0[8], 0.5 * state0[7], -0.5 * state0[6], 0]]) # System matrix

B = np.array([[1/m, 0, 0, 0, 0, 0],
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
              [0, 0, 0, 0, 0, 0]]) # Control matrix. Note: m = mass, Ii = inverse inertia matrix

state_d = np.dot(A, state0) + np.dot(B, U) # State derivative vector [u_d, v_d, w_d, x_d, y_d, z_d, phi_dd, theta_dd, psi_dd, qw_d, qx_d, qy_d, qz_d]
```

- Full 6dof state space model of Vessel and CelestialBody objects.
- Includes methods for PID control of state variables.
- Simulate rocket launch.
- Simulate satellite orbits.
- Simulate complex systems of multiple Vessel and CelestialBody objects.
- Get initial conditions from Two Line Elements

See ISS_example.py, Falcon9_example.py, EarthMoon_example.py for example applications.
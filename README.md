# rocketsim
Python package for simulating space vehicles from launch to orbit.

Supports 6dof state space model of Vessel objects as well as multiple CelestialBody objects. Includes methods for PID control of state variables.

To do:
- Improve Iz calculation for vessels
- Aerodynamics module to simulate atmospheric effects
- Plotting helper functions [STARTED]

Complete:
- Enable simulation of multiple body objects (i.e. to simulate n-body problems)
- Update body and vehicle objects so that state is saved on the objects instead of in numpy arrays in scripts
- Update body and vehicle objects to store u vector over time in same way state is stored
- Optimize appending on objects since this seems to be slowing things down
- Implement getForceTorque() functions on body and vehicle objects
- Update thrust function for 6dof
- Update doc strings to account for use of quaternions in state vector
- Full 6dof capabilities with multiple bodies for simulation of Earth - Moon transfers for example
- Add System class and implement method of simulating full system (i.e. not needing to simulate individual objects)
- Full doc strings for classes and methods

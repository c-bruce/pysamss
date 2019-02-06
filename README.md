# rocketsim
Python package for simulating space vehicles from launch to orbit. Supports 3dof state space models of launch vehicles and satellites. Includes methods for PID control of state variables.

"referenceFrame" objects represent 2D reference frames.

"body" objects can be used to represent celestial bodies like the Earth, Moon, Sun etc. Each body has it's own reference frame.

"vehicle" objects can be used to represent and simulate launch vehicles or satellites. Vehicles are made up of "stage" objects. Each vehicle has it's own reference frame.

To do:
- Improve Iz calculation for vehicles
- Full doc strings for classes and methods
- Aerodynamics module to simulate atmospheric effects
- Full 6dof capabilities with multiple bodies for simulation of Earth - Moon transfers for example
- Plotting helper functions
- Update body and vehicle objects to store u vector over time in same way state is stored
- Add System class and implement method of simulating full system (i.e. not needing to simulate individual objects)
- Implement getForceTorque() functions on body and vehicle objects
- Optimise appending on objects since this seems to be slowing things down

Complete:
- Enable simulation of multiple body objects (i.e. to simulate n-body problems) [DONE]
- Update body and vehicle objects so that state is saved on the objects instead of in numpy arrays in scripts [DONE]

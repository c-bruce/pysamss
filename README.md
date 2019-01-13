# rocketsim
Python package for simulating space vehicles from launch to orbit. Supports 3dof state space models of launch vehicles and satellites. Includes methods for PID control of state variables.

"referenceFrame" objects represent 2D reference frames.

"body" objects can be used to represent celestial bodies like the Earth, Moon, Sun etc. Each body has it's own reference frame.

"vehicle" objects can be used to represent and simulate launch vehicles. Vehicles are made up of "stage" objects. Each vehicle has it's own reference frame.

To do:
- Enable simulation of multiple body objects (i.e. to simulate n-body problems)
- Improve Iz calculation for vehicles
- Full doc strings for classes and methods
- Update body and vehicle objects so that state is saved on the objects instead of in numpy arrays in scripts
- Aerodynamics module to simulate atmospheric effects
- Full 6dof capabilities with multiple bodies for simulation of Earth - Moon transfers for example

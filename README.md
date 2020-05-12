# pySAMSS

Python Space Asset Management and Simulation System

A Python package for managing and simulating assets in Space.

![alt text](https://github.com/c-bruce/pysamss/blob/master/examples/ISS_example.png "pySAMSS - ISS Example")

# Introduction

pySAMSS provides a full 6 degree of freedom state space model representation of CelestialBody and Vessel objects. Using a numerical integration scheme (i.e. Euler or RK4) the future state of CelestialBody and Vessel objects can be found explicitly where:

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

# Installation

To install the latest development version of pySAMSS first make sure you have git installed, see [here](https://git-scm.com/downloads), then clone the repository:

```
git clone https://github.com/c-bruce/pysamss.git
```

Next, build the .tar.gz distributable:

```
python setup.py sdist
```

Finally, cd into the ./dist/ folder and install using pip:

```
pip install pysamss-0.0.1.tar.gz
```

# Using pySAMSS

Begin by creating a System instance and add CelestialBody and Vessel objects to the current Timestep:

```python
# Create System instance
system = pysamss.System('EarthMoonISS')

# Add CelestialBody objects to system
system.current.addCelestialBody(pysamss.CelestialBody('Earth', 5.972e24, 6.371e6))
system.current.addCelestialBody(pysamss.CelestialBody('Moon', 7.348e22, 1.737e6, parent_name='Earth'))

# Add Vessel objects to system
system.current.addVessel(pysamss.Vessel('ISS', [pysamss.Stage(419725, 1, 10, np.array([0, 0, 0]))], parent_name='Earth'))
```

Define and set initial conditions for CelestialBody objects. This can be done convieniently using the [jplephem](https://pypi.org/project/jplephem/) package which can load and use ephemeris from NASA's Jet Propulsion Laboratory:

```python
time = system.current.getJulianDate()
kernel = SPK.open('de430.bsp')
# Earth
earth_pos, earth_vel = kernel[3,399].compute_and_differentiate(time)
earth_pos *= 1000 # Convert from km -> m
earth_vel /= 86.4 # Convert from km/day -> m/s
system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
# Moon
moon_pos, moon_vel = kernel[3,301].compute_and_differentiate(time)
moon_pos *= 1000 # Convert from km -> m
moon_vel /= 86.4 # Convert from km/day -> m/s
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
```

Define and set initial conditions for Vessel objects. This can be done convieniently using the [spk4](https://pypi.org/project/sgp4/) package which takes Two Line Element (TLE) data from [CelesTrak](http://celestrak.com/) and returns position and velocity vectors relative to the Earth-centered inertial coordinate system:

```python
# Get TLE data from CelesTrak
http = urllib3.PoolManager()
tle = http.request('GET', 'https://www.celestrak.com/NORAD/elements/stations.txt')
tle = tle.data.decode('utf-8').strip().split('\r\n') # Gets full TLE's for constelation into a list
# ISS
time = np.modf(time) # Split Julian date into integer and decimal for spg4 library
iss_tle = tle[0:3]
iss = Satrec.twoline2rv(iss_tle[1], iss_tle[2])
e, iss_pos, iss_vel = iss.sgp4(time[1], time[0])
iss_pos = np.array(iss_pos) * 1000
iss_vel = np.array(iss_vel) * 1000
system.current.vessels['ISS'].setPosition(iss_pos, local=True)
system.current.vessels['ISS'].setVelocity(iss_vel, local=True)
```

Set system timestep, end time, save interval and run the simulation:

```python
# Simulate system
system.setDt(0.1)
system.setEndTime(5561.0)
system.setSaveInterval(10)
system.simulateSystem()
```

All simulation data is written out to *.h5 files saved in the *_data directory. Once a simulation is complete this data can be read and post processed. pySAMSS comes with an interactive widget, based on [mayavi](https://docs.enthought.com/mayavi/mayavi/), for visually post processing simulation data:

```python
# Load system data
system.load('EarthMoonISS.psm')

# Get data
iss_pos = system.timestep[100].vessels['ISS'].getPosition()

# Visual post processing
fig = pysamss.MainWidget()
fig.loadSystem(system)
fig.showMaximized()
mlab.show()
```

See the [examples](https://github.com/c-bruce/pysamss/tree/master/examples) directory for more pySAMSS examples. 

Notes:

- The System class currently only supports a gravity as a force/torque source. See "Future Developments" for information on how this will change in the future.

- CelestialBody and Vessel objects can be used and simulated independently. Falcon9_example.py shows an example of how this can be achieved - in this example, a Vessel "falcon9", has two force/torque sources - gravity and thrust. The Vessels orientation over time is controlled using a pitch PID controller. A disadvantage of this approach is that the user is required to manually set up all reference frames and relationships between objects - this is usually automatically handled by the System and Timestep classes.

# Limitations

pySAMSS is currently in an early stage of development and as such there are a number of limitations, such as:

- Performance (pySAMSS is currently not optimized for speed)
- System class only includes gravity force/torque source
- No aerodynamic force/torque source
- Not able to use controllers inside System class

# Future Developments

In no particular order here is a list of some planned future developments:

- GroundStation class (to be able to do coverage analysis etc.)
- Maneuver class (for maneuver/mission planning)
- FlightProgram class (to support a series of Maneuvers for a given Vessel similar to Falcon9_example.py)
- Aerodynamics force/torque source
- Performance optimization
- Support for advanced gravity models
- Automatically define CelestialBody orientations at a given datetime (i.e. due to rotation speed)
- Update parent CelestialBody depending on current sphere of influence
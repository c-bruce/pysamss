# Date: 20/11/2022
# Author: Callum Bruce
# Earth, Moon, Orion example. Orion initial conditions from https://twitter.com/NASA_Orion
# Start time = 2022-11-16 20:52:00
# To run, ensure 'de430.bsp' is downloaded to the working directory. See https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/.
import numpy as np
import datetime
from jplephem.spk import SPK
import pysamss

# Step 1: Setup system
# Mission Time: 0 days, 22  hrs, 5  min
# Orion is 109,415 miles from Earth, 179,171 miles from the Moon, cruising at 3,412 miles per hour.
P = [-110039, -27010, -3928]
V = [-3011, -1506, -555]
# O: 55º, 56.7º, 21.2º
system = pysamss.System('EarthMoonOrion_Pt5')
launch_time = datetime.datetime(2022, 11, 16, 6, 47, 44)
time_delta = datetime.timedelta(hours=22, minutes=5)
system.current.setDatetime(launch_time + time_delta)

# Step 1.1: Add Earth, Moon and ISS to system
system.current.addCelestialBody(pysamss.CelestialBody('Earth', 5.972e24, 6.371e6))
system.current.addCelestialBody(pysamss.CelestialBody('Moon', 7.348e22, 1.737e6, parent_name='Earth'))
system.current.addVessel(pysamss.Vessel('Orion', [pysamss.Stage(33446, 1, 10, np.array([0, 0, 0]))], parent_name='Earth'))

# Step 2: Calculate positions and velocities
time = system.current.getJulianDate()
kernel = SPK.open('de430.bsp')
# Earth
earth_pos, earth_vel = kernel[3,399].compute_and_differentiate(time)
earth_pos *= 1000 # Convert from km -> m
earth_vel /= 86.4 # Convert from km/day -> m/s
# Moon
moon_pos, moon_vel = kernel[3,301].compute_and_differentiate(time)
moon_pos *= 1000 # Convert from km -> m
moon_vel /= 86.4 # Convert from km/day -> m/s
# Orion
orion_pos = (np.array(P) * 1609.34) + earth_pos
orion_vel = (np.array(V) * 0.44704) + earth_vel

# Step 3: Set positions and velocities
system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Earth'].setAttitudeDot(np.array([0.0, 0.0, np.deg2rad(360 / ((23 * 60 * 60) + (56 * 60) + 4))]))
system.current.celestial_bodies['Earth'].setTexture(pysamss.__file__[:-12] + '/resources/earth.jpg')
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.celestial_bodies['Moon'].setAttitudeDot(np.array([0.0, 0.0, np.deg2rad(360 / 2358720.0)]))
system.current.celestial_bodies['Moon'].setTexture(pysamss.__file__[:-12] + '/resources/moon.jpg')
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

# Step 4: Simulate system
system.setDt(0.1)
system.setEndTime(14401)
system.setSaveInterval(10)
system.simulateSystem()

# Step 5: Post processing
orion_V = system.current.vessels['Orion'].getVelocity()

earth_orion_P = system.current.vessels['Orion'].getPosition() - system.current.celestial_bodies['Earth'].getPosition()
earth_orion_separation = np.sqrt(sum(earth_orion_P**2))
earth_radius = system.current.celestial_bodies['Earth'].getRadius()

moon_orion_P = system.current.vessels['Orion'].getPosition() - system.current.celestial_bodies['Moon'].getPosition()
moon_orion_separation = np.sqrt(sum(moon_orion_P**2))
moon_radius = system.current.celestial_bodies['Moon'].getRadius()

print(f"Earth - Orion: {(earth_orion_separation - earth_radius) * 0.000621371} [miles]")
print(f"Moon - Orion: {(moon_orion_separation - moon_radius) * 0.000621371} [miles]")
print(f"P: {earth_orion_P * 0.000621371} [miles]")
print(f"V: {orion_V * 2.23694} [miles/hour]")

# Results:
# Earth - Orion: 121946.9853191543 [miles]
# Moon - Orion: 173291.03193064677 [miles]
# P: [-121389.06206752  -32855.89909097   -6118.8937077 ] [miles]
# V: [-2665.07616458 -1396.53577173  -529.5053399 ] [miles/hour]
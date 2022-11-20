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
# Mission Time: 1 days, 6  hrs, 5  min
# Orion is 133,284 miles from Earth, 167,668 miles from the Moon, cruising at 2,799 miles per hour.
P = [-131510, -38375, -8248]
V = [-2400, -1341, -525]
# O: 53º, 53.5º, 18.0º
system = pysamss.System('EarthMoonOrion_Pt7')
launch_time = datetime.datetime(2022, 11, 16, 6, 47, 44)
time_delta = datetime.timedelta(days=1, hours=6, minutes=5)
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
orion_vel = np.array(V) * 0.44704

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
# Earth - Orion: 143703.11863792257 [miles]
# Moon - Orion: 162259.34260912964 [miles]
# P: [-140671.65404456  -43683.18495251  -10358.27789796] [miles]
# V: [-2167.7212421  -1269.06108136  -508.19058034] [miles/hour]
# Date: 20/11/2022
# Author: Callum Bruce
# Earth, Moon, Orion example. Orion initial conditions from https://twitter.com/NASA_Orion
# Time of corrections and manoeuvres from https://blogs.nasa.gov/artemis/
# 1st correction @ 1532 UTC Nov 16 2022 datetime.datetime(2022, 11, 16, 15, 32, 00)
# 2nd correction @ 1132 UTC Nov 17 2022 datetime.datetime(2022, 11, 17, 11, 32, 00)
# 3rd correction @ 1212 UTC Nov 20 2022 datetime.datetime(2022, 11, 20, 12, 12, 00)
# 4th correction @ 0744 UTC Nov 21 2022 datetime.datetime(2022, 11, 21, 07, 44, 00)
# Powered flyby @ 1244 UTC Nov 21 2022 datetime.datetime(2022, 11, 21, 12, 44, 00)
# 5th correction @ 0602 UTC Nov 22 2022 datetime.datetime(2022, 11, 22, 06, 02, 00)
# 6th correction @ 2152 UTC Nov 24 2022 datetime.datetime(2022, 11, 24, 21, 52, 00)
# Distant retrograde insertion @ 2200 UTC Nov 25 2022 datetime.datetime(2022, 11, 25, 22, 52, 00)
# 1st orbital maintenance burn @ 2152 UTC Nov 26 2022 datetime.datetime(2022, 11, 26, 21, 52, 00)

# 2nd orbital maintenance burn @ ?
# Distant retrograde orbit departure burn @ 2153 UTC Dec 01 2022 datetime.datetime(2022, 12, 1, 21, 53, 00)
# 1st trajectory correction burn @ 0353 UTC Dec 02 2022 datetime.datetime(2022, 12, 2, 03, 53, 00)
# 2nd trajectory correction burn @ 1643 UTC Dec 04 2022 datetime.datetime(2022, 12, 4, 16, 43, 00)
# 3rd trajectory correction burn @ 1043 UTC Dec 05 2022 datetime.datetime(2022, 12, 5, 10, 43, 00)
# Powered flyby burn @ 1643 UTC Dec 05 2022 datetime.datetime(2022, 12, 5, 16, 43, 00)
# 4th trajectory correction burn @ 1043 UTC Dec 06 2022 datetime.datetime(2022, 12, 6, 10, 43, 00)

import numpy as np
import datetime
from jplephem.spk import SPK
import pysamss

# Step 1: Setup system
# Mission Time: 0 days, 1  hrs, 59  min
# Orion is 3,149 miles from Earth, 242,856 miles from the Moon, cruising at 18,399 miles per hour.
P = [-2280, 5716, 3557]
V = [-17235, 4592, 4514]
# O: 66º, 47.3º, 244.4º
system = pysamss.System('EarthMoonOrion')
launch_time = datetime.datetime(2022, 11, 16, 6, 47, 00)
#time_delta = datetime.timedelta(hours=1, minutes=59)
system.current.setDatetime(launch_time + datetime.timedelta(hours=1, minutes=59))

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
# Leg 1
end_time = int((datetime.timedelta(hours=10, minutes=5) - datetime.timedelta(hours=1, minutes=59)).total_seconds())
system.setDt(1)
system.setEndTime(end_time)
system.setSaveInterval(300)
system.simulateSystem()

# Leg 2 - Starting after 1st correction
# Mission Time: 0 days, 10  hrs, 5  min
# Orion is 61,078 miles from Earth, 201,852 miles from the Moon, cruising at 5,281 miles per hour.
P = [-64593, -7035, 2841]
V = [-4918, -1844, -547]
# O: 63º, 45.4º, 350.5º

# Update Orion position and velocity
# earth_pos = system.current.celestial_bodies['Earth'].getPosition()
# earth_vel = system.current.celestial_bodies['Earth'].getVelocity()
# orion_pos = (np.array(P) * 1609.34) + earth_pos
# orion_vel = (np.array(V) * 0.44704) + earth_vel

# system.current.vessels['Orion'].setPosition(orion_pos)
# system.current.vessels['Orion'].setVelocity(orion_vel)
system.current.setDatetime(launch_time + datetime.timedelta(hours=10, minutes=5))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=1, hours=6, minutes=5) - datetime.timedelta(hours=10, minutes=5)).total_seconds())
#leg2_EndTime = int((datetime.timedelta(days=1, hours=6, minutes=5) - datetime.timedelta(hours=10, minutes=5)).total_seconds()) + leg1_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 3 - Starting after 2nd correction
# Mission Time: 1 days, 6  hrs, 5  min
# Orion is 133,284 miles from Earth, 167,668 miles from the Moon, cruising at 2,799 miles per hour.
P = [-131510, -38375, -8248]
V = [-2400, -1341, -525]
# O: 53º, 53.5º, 18.0º

# Update Orion position and velocity
# earth_pos = system.current.celestial_bodies['Earth'].getPosition()
# earth_vel = system.current.celestial_bodies['Earth'].getVelocity()
# orion_pos = (np.array(P) * 1609.34) + earth_pos
# orion_vel = (np.array(V) * 0.44704) + earth_vel

# system.current.vessels['Orion'].setPosition(orion_pos)
# system.current.vessels['Orion'].setVelocity(orion_vel)
system.current.setDatetime(launch_time + datetime.timedelta(days=1, hours=6, minutes=5))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=4, hours=8, minutes=37) -  datetime.timedelta(days=1, hours=6, minutes=5)).total_seconds())
#leg3_EndTime = int((datetime.timedelta(days=4, hours=8, minutes=37) -  datetime.timedelta(days=1, hours=6, minutes=5)).total_seconds()) + leg2_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 4 - Starting after 3rd correction
# Mission Time: 4 days, 8  hrs, 37  min
# Orion is 231,547 miles from Earth, 47,431 miles from the Moon, cruising at 455 miles per hour.
P = [-209971, -100340, -36150]
V = [-153, -373, -211]
# O: 52º, 56.1º, 15.0º
# earth_pos = system.current.celestial_bodies['Earth'].getPosition()
# earth_vel = system.current.celestial_bodies['Earth'].getVelocity()
# orion_pos = (np.array(P) * 1609.34) + earth_pos
# orion_vel = (np.array(V) * 0.44704) + earth_vel

# system.current.vessels['Orion'].setPosition(orion_pos)
# system.current.vessels['Orion'].setVelocity(orion_vel)
system.current.setDatetime(launch_time + datetime.timedelta(days=4, hours=8, minutes=37))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=5, hours=4, minutes=0) - datetime.timedelta(days=4, hours=8, minutes=37)).total_seconds())
#leg4_EndTime = int((datetime.timedelta(days=5, hours=4, minutes=0) - datetime.timedelta(days=4, hours=8, minutes=37)).total_seconds()) + leg3_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 5 - Starting after 4th correction
# Mission Time: 5 days, 4  hrs, 0  min
# Orion is 233,303 miles from Earth, 5,875 miles from the Moon, cruising at 547 miles per hour.
P = [-210291, -103034, -38142]
V = [41, 503, 212]
# O: 58º, 50.5º, 9.9º
# earth_pos = system.current.celestial_bodies['Earth'].getPosition()
# earth_vel = system.current.celestial_bodies['Earth'].getVelocity()
# orion_pos = (np.array(P) * 1609.34) + earth_pos
# orion_vel = (np.array(V) * 0.44704) + earth_vel

# system.current.vessels['Orion'].setPosition(orion_pos)
# system.current.vessels['Orion'].setVelocity(orion_vel)
system.current.setDatetime(launch_time + datetime.timedelta(days=5, hours=4, minutes=0))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=5, hours=6, minutes=40) - datetime.timedelta(days=5, hours=4, minutes=0)).total_seconds())
#leg5_EndTime = int((datetime.timedelta(days=5, hours=6, minutes=40) - datetime.timedelta(days=5, hours=4, minutes=0)).total_seconds()) + leg4_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 6 - Starting after powered flyby
# Mission Time: 5 days, 6  hrs, 40  min
# Orion is 228,682 miles from Earth, 962 miles from the Moon, cruising at 4,861 miles per hour.
P = [-206857, -99836, -36936]
V = [4780, -552, -693]
# O: 60º, 60.8º, 19.8º
# earth_pos = system.current.celestial_bodies['Earth'].getPosition()
# earth_vel = system.current.celestial_bodies['Earth'].getVelocity()
# orion_pos = (np.array(P) * 1609.34) + earth_pos
# orion_vel = (np.array(V) * 0.44704) + earth_vel

# system.current.vessels['Orion'].setPosition(orion_pos)
# system.current.vessels['Orion'].setVelocity(orion_vel)
system.current.setDatetime(launch_time + datetime.timedelta(days=5, hours=6, minutes=40))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=5, hours=9, minutes=0) - datetime.timedelta(days=5, hours=6, minutes=40)).total_seconds())
#leg6_EndTime = int((datetime.timedelta(days=5, hours=9, minutes=0) - datetime.timedelta(days=5, hours=6, minutes=40)).total_seconds()) + leg5_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 6.5 - Manual exit moon correction THIS IS NOT FOLLOWING A REAL ORBITAL CORRECTION
# Mission Time: 5 days, 9  hrs, 0  min
# Orion is 223,032 miles from Earth, 5,982 miles from the Moon, cruising at 3,930 miles per hour.
P = [-198101, -103527, -39535]
V = [3213, -1902, -1226]
# O: 59º, 58.8º, 19.8º
system.current.setDatetime(launch_time + datetime.timedelta(days=5, hours=9, minutes=0))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=6, hours=2, minutes=1) - datetime.timedelta(days=5, hours=9, minutes=0)).total_seconds())
#leg6_5_EndTime = int((datetime.timedelta(days=6, hours=2, minutes=1) - datetime.timedelta(days=5, hours=9, minutes=0)).total_seconds()) + leg6_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 7 - Starting after 5th correction
# Mission Time: 6 days, 2  hrs, 1  min
# Orion is 210,096 miles from Earth, 25,858 miles from the Moon, cruising at 3,190 miles per hour.
P = [-154278, -135970, -59410]
V = [2417, -1775, -1087]
# O: 58º, 54.0º, 11.2º
# earth_pos = system.current.celestial_bodies['Earth'].getPosition()
# earth_vel = system.current.celestial_bodies['Earth'].getVelocity()
# orion_pos = (np.array(P) * 1609.34) + earth_pos
# orion_vel = (np.array(V) * 0.44704) + earth_vel

# system.current.vessels['Orion'].setPosition(orion_pos)
# system.current.vessels['Orion'].setVelocity(orion_vel)
system.current.setDatetime(launch_time + datetime.timedelta(days=6, hours=2, minutes=1))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=8, hours=15, minutes=55) - datetime.timedelta(days=6, hours=2, minutes=1)).total_seconds())
#leg7_EndTime = int((datetime.timedelta(days=8, hours=15, minutes=55) - datetime.timedelta(days=6, hours=2, minutes=1)).total_seconds()) + leg6_5_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 8 - Starting after 6th correction
# Mission Time: 8 days, 15  hrs, 55  min
# Orion is 225,071 miles from Earth, 56,510 miles from the Moon, cruising at 2,573 miles per hour.
P = [1134, -203551, -104979]
V = [2516, -384, -379]
# O: 282º, 141.7º, 138.8º
# earth_pos = system.current.celestial_bodies['Earth'].getPosition()
# earth_vel = system.current.celestial_bodies['Earth'].getVelocity()
# orion_pos = (np.array(P) * 1609.34) + earth_pos
# orion_vel = (np.array(V) * 0.44704) + earth_vel

# system.current.vessels['Orion'].setPosition(orion_pos)
# system.current.vessels['Orion'].setVelocity(orion_vel)
system.current.setDatetime(launch_time + datetime.timedelta(days=8, hours=15, minutes=5))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=9, hours=16, minutes=27) - datetime.timedelta(days=8, hours=15, minutes=55)).total_seconds())
#leg8_EndTime = int((datetime.timedelta(days=9, hours=16, minutes=27) - datetime.timedelta(days=8, hours=15, minutes=55)).total_seconds()) + leg7_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 9 - Starting after distant retrograde insertion
# Mission Time: 9 days, 16  hrs, 27  min
# Orion is 238,705 miles from Earth, 57,127 miles from the Moon, cruising at 2,238 miles per hour.
P = [60767, -207026, -111055]
V = [2227, -91, -204]
# O: 289º, 132.4º, 147.7º
system.current.setDatetime(launch_time + datetime.timedelta(days=9, hours=16, minutes=27))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=10, hours=16, minutes=27) - datetime.timedelta(days=9, hours=16, minutes=27)).total_seconds())
#leg9_EndTime = int((datetime.timedelta(days=10, hours=16, minutes=27) - datetime.timedelta(days=9, hours=16, minutes=27)).total_seconds()) + leg8_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 10 - Starting after 1st orbital maintenance burn
# Mission Time: 10 days, 16  hrs, 27  min
# Orion is 254,457 miles from Earth, 51,646 miles from the Moon, cruising at 1,972 miles per hour.
P = [110998, -204128, -113091]
V = [1945, 323, 30]
# O: 280º, 130.8º, 146.4º
system.current.setDatetime(launch_time + datetime.timedelta(days=10, hours=16, minutes=27))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=13, hours=14, minutes=8) - datetime.timedelta(days=10, hours=16, minutes=27)).total_seconds())
#leg10_EndTime = int((datetime.timedelta(days=15, hours=15, minutes=21) - datetime.timedelta(days=10, hours=16, minutes=27)).total_seconds()) + leg9_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 10.5 - 
# Mission Time: 13 days, 14  hrs, 8  min
# Orion is 264,582 miles from Earth, 45,691 miles from the Moon, cruising at 1,782 miles per hour.
P = [208964, -143491, -88648]
V = [843, 1418, 673]
# O: 308º, 121.6º, 189.3º
system.current.setDatetime(launch_time + datetime.timedelta(days=13, hours=16, minutes=27))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=15, hours=15, minutes=21) - datetime.timedelta(days=13, hours=14, minutes=8)).total_seconds())
system.setEndTime(end_time)
system.simulateSystem()

# Leg 11 - Starting after distant retrograde orbit departure burn
# Mission Time: 15 days, 15  hrs, 21  min
# Orion is 237,751 mi from Earth, 52,949 mi from the Moon, cruising at 2,329 mph. 
P = [230524, -56744, -45414]
V = [303, 2049, 1066]
# O: 283º, 114º, 159º
system.current.setDatetime(launch_time + datetime.timedelta(days=15, hours=15, minutes=21))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=15, hours=23, minutes=47) - datetime.timedelta(days=15, hours=15, minutes=21)).total_seconds())
#leg11_EndTime = int((datetime.timedelta(days=15, hours=23, minutes=47) - datetime.timedelta(days=15, hours=15, minutes=21)).total_seconds()) + leg10_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 12 - Starting after 1st trajectory correction burn
# Mission Time: 15 days, 23  hrs, 47  min
# Orion is 234,429 mi from Earth, 52,456 mi from the Moon, cruising at 2,404 mph. 
P = [232352, -39130, -36199]
V = [128, 2125, 1117]
# O: 288º, 128º, 144º
system.current.setDatetime(launch_time + datetime.timedelta(days=15, hours=23, minutes=47))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=18, hours=11, minutes=39) - datetime.timedelta(days=15, hours=23, minutes=47)).total_seconds())
#leg12_EndTime = int((datetime.timedelta(days=18, hours=11, minutes=39) - datetime.timedelta(days=15, hours=23, minutes=47)).total_seconds()) + leg11_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 13 - Starting after 2nd trajectory correction burn
# Mission Time: 18 days, 11  hrs, 39  min
# Orion is 221,272 mi from Earth, 27,195 mi from the Moon, cruising at 3,011 mph. 
P = [199265, 97817, 38138]
V = [-1231, 2403, 1333]
# O: 321º, 148º, 110º
system.current.setDatetime(launch_time + datetime.timedelta(days=18, hours=11, minutes=39))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=19, hours=7, minutes=39) - datetime.timedelta(days=18, hours=11, minutes=39)).total_seconds())
#leg13_EndTime = int((datetime.timedelta(days=19, hours=7, minutes=39) - datetime.timedelta(days=18, hours=11, minutes=39)).total_seconds()) + leg12_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 14 - Starting after 3rd trajectory correction burn
# Mission Time: 19 days, 7  hrs, 39  min
# Orion is 234,227 mi from Earth, 4,858 mi from the Moon, cruising at 3,957 mph. 
P = [172326, 150364, 66536]
V = [-1102, 3418, 1662]
# O: 29º, 17º, 319º
system.current.setDatetime(launch_time + datetime.timedelta(days=19, hours=7, minutes=39))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=19, hours=11, minutes=39) - datetime.timedelta(days=19, hours=7, minutes=39)).total_seconds())
#leg14_EndTime = int((datetime.timedelta(days=19, hours=11, minutes=39) - datetime.timedelta(days=19, hours=7, minutes=39)).total_seconds()) + leg13_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 15 - Starting after powered flyby burn
# Mission Time: 19 days, 11  hrs, 39  min
# Orion is 243,167 mi from Earth, 5,132 mi from the Moon, cruising at 1,202 mph. 
P = [175493, 159868, 68671]
V = [1001, 17, -666]
# O: 25º, 15º, 313º
system.current.setDatetime(launch_time + datetime.timedelta(days=19, hours=11, minutes=39))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=20, hours=7, minutes=41) - datetime.timedelta(days=19, hours=11, minutes=39)).total_seconds())
#leg15_EndTime = int((datetime.timedelta(days=20, hours=7, minutes=41) - datetime.timedelta(days=19, hours=11, minutes=39)).total_seconds()) + leg14_EndTime
system.setEndTime(end_time)
system.simulateSystem()

# Leg 16 - Starting after 4th trajectory correction burn
# Mission Time: 20 days, 7  hrs, 41  min
# Orion is 245,975 mi from Earth, 57,329 mi from the Moon, cruising at 448 mph. 
P = [181642, 161032, 59512]
V = [47, -18, -445]
# O: 16º, 15º, 309º
system.current.setDatetime(launch_time + datetime.timedelta(days=20, hours=7, minutes=41))
time = system.current.getJulianDate()
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

system.current.celestial_bodies['Earth'].setPosition(earth_pos)
system.current.celestial_bodies['Earth'].setVelocity(earth_vel)
system.current.celestial_bodies['Moon'].setPosition(moon_pos)
system.current.celestial_bodies['Moon'].setVelocity(moon_vel)
system.current.vessels['Orion'].setPosition(orion_pos)
system.current.vessels['Orion'].setVelocity(orion_vel)

end_time += int((datetime.timedelta(days=25, hours=6, minutes=9) - datetime.timedelta(days=20, hours=7, minutes=41)).total_seconds())
#leg16_EndTime = 2000000#int((datetime.timedelta(days=20, hours=7, minutes=41) - datetime.timedelta(days=19, hours=11, minutes=39)).total_seconds()) + leg14_EndTime
system.setEndTime(end_time)
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
# Earth - Orion: 61032.68112835576 [miles]
# Moon - Orion: 202027.69764029287 [miles]
# P: [-64533.65990938  -7188.84465385   2759.3431476 ] [miles]
# V: [-4878.72072754 -1888.10892566  -571.89357244] [miles/hour]

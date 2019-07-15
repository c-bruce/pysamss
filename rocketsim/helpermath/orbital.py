# Date: 15/07/2019
# Author: Callum Bruce
# Helper functions for converting between cartesian and orbital elements
import numpy as np
import scipy

def orbitalelements2cartesian(a, e, omega, LAN, i, M0, t0, t, obj0):
    """
    Convert orbital elements to cartesian coordinates.

    Args:
        a (float): Semi-major axis [m].
        e (float): Eccentricity.
        omega (float): Argument of periapsis [rad].
        LAN (float): Longitude of assending node [rad].
        i (float): Inclination [rad].
        M0 (float): Mean anomaly [rad] at epoch t0 [JD].
        t0 (float): Epoch at t = 0 [JD].
        t (float): Considered epoch [JD].
        obj0 (obj): Primary CelestialBody object.

    Returns:
        position (np.array): Position vector x, y, z [m].
        velocity (np.array): Velocity vector u, v, w [m].
    """
    # See https://downloads.rene-schwarz.com/download/M001-Keplerian_Orbit_Elements_to_Cartesian_State_Vectors.pdf
    # Step 1: Calculate standard gravitational parameter, mu
    G = 6.67408e-11 # Gravitational constant [m**3.kg**-1.s**-2]
    mu = G * obj0.getMass() # Standard gravitational parameter [m**3.s**-2]
    # Step 2: Calculate mean anomaly, M_t in seconds
    if t != t0:
        delta_t = 86400 * (t - t0)
        M_t = M0 + delta_t * np.sqrt(mu / a**3) # Mean anomaly
        M_t = np.arctan(sin(M_t - np.pi), cos(M_t - np.pi)) + np.pi # Map M_t to values between 0 -> 2 * pi
    else:
        M_t = M0
    # Step 3: Solve Keplers Equation M(t) = E(t) - e * sin(E(t))
    f = lambda E : E - e * np.sin(E) - M_t
    E0 = M_t
    E_t = scipy.optimize.newton(f, E0, tol=1e-12) # Solve for E using Newton-Raphson
    # Step 4: Obtain true anomaly, v_t
    v_t = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E_t / 2), np.sqrt(1 - e) * np.cos(E_t / 2))
    # Step 5: Get distance to obj0, r_t
    r_t = a * (1 - e * np.cos(E_t))
    # Step 6: Calculate position and velocity vectors in the orbital frame
    # (z-axis perpendicular to orbital plane, x-axis pointing to periapsis of the orbit)
    position = r_t * np.array([np.cos(v_t), np.sin(v_t), 0])
    velocity = (np.sqrt(mu * a) / r_t) * np.array([-np.sin(E_t), np.sqrt(1 - e**2) * np.cos(E_t), 0])
    # Step 7: Transform position and velocity to the inertial frame
    Rx = lambda phi : np.array([[1, 0, 0], [0, np.cos(phi), -np.sin(phi)], [0, np.sin(phi), np.cos(phi)]])
    Rz = lambda psi : np.array([[np.cos(psi), -np.sin(psi), 0], [np.sin(psi), np.cos(psi), 0], [0, 0, 1]])
    R = np.matmul(Rz(-LAN), np.matmul(Rx(-i), Rz(-omega)))
    position = np.dot(R, position)
    velocity = np.dot(R, velocity)

def cartesian2orbitalelements():
    """
    Convert cartesian coordinates to orbital elements.
    """

# Date: 06/01/2019
# Author: Callum Bruce
# Stage Class
import numpy as np

class Stage:
    """
    Stage class.

    Args:
        mass (float): Stage mass (kg).
        radius (float): Stage radius (m).
        length (float): Stage length (m).
        position (np.array): Stage position relative to Vessel bodyRF np.array([x,y,z]) (m).

    Note:
        - Stage objects are assumed cylindrical with CoT 0.5 * length aft of
          position.
        - drymass = 0.05 * mass, wetmass = 0.95 * mass.
    """
    def __init__(self, mass, radius, length, position):
        self.mass = mass
        self.drymass = 0.05 * mass
        self.wetmass = 0.95 * mass
        self.radius = radius
        self.length = length
        self.position = position
        self.gimbal = np.array([0, 0]) # [theta, psi]

    def updateMass(self, m_dot):
        """
        Update wetmass and mass due to fuel burn m_dot.

        Args:
            m_dot (float): Mass delta -ive denotes fuel burnt.
        """
        if self.wetmass > 0:
            wetmass = self.wetmass + m_dot
            self.wetmass = wetmass
            mass = self.drymass + self.wetmass
            self.mass = mass

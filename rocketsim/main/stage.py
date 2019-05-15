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
        position (list): Stage position relative to referenceFrame [x,y] (m).

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
        self.position = np.array(position)
        self.gimbal = [0, 0] # [theta, psi]

    def updateMass(self, m_dot):
        """
        Update wetmass and mass due to fuel burn m_dot.

        Args:
            m_dot (float): Mass delta -ive denotes fuel burnt.
        """
        wetmass = self.wetmass + m_dot
        self.wetmass = wetmass
        mass = self.drymass + self.wetmass
        self.mass = mass

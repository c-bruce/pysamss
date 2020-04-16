# Date: 06/01/2019
# Author: Callum Bruce
# RigidBody Class
import numpy as np
from .referenceframe import ReferenceFrame
from ..helpermath.helpermath import *

class RigidBody:
    """
    RigidBody class.

    Args:
        name (str): RigidBody name.
        state (np.array): State vector [u, v, w, x, y, z, phi_d, theta_d, psi_d, qw, qx, qy, qz].
        U (np.array): U vector [Fx, Fy, Fz, Mx, My, Mz].
        parent_name (str): Name of parent RigidBody object.

    Note:
        - CelestialBody and Vessel classes derive the bulk of their methods
          from RigidBody class.
    """
    def __init__(self, name, state=None, U=None, parent_name=None):
        self.name = name
        if state is None:
            self.state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
        else:
            self.state = state
        if U is None:
            self.U = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        else:
            self.U = U
        self.universalRF = None
        self.parentRF = None
        self.bodyRF = None
        self.parent_name = parent_name
        self.parent = None

    def getState(self):
        """
        Get current state vector.
        [u, v, w, x, y, z, phi_d, theta_d, psi_d, qw, qx, qy, qz]

        Returns:
            state (list): Current state vector.
        """
        return self.state

    def setState(self, state):
        """
        Set current state vector.
        [u, v, w, x, y, z, phi_d, theta_d, psi_d, qw, qx, qy, qz]

        Args:
            state (list): State vector to set.
        """
        self.state = state

    def getVelocity(self, local=None):
        """
        Get current velocity vector.
        [u, v, w]

        Args:
            local (bool): If true velocity is relative to parentRF. Else
                          velocity is relative to universalRF.

        Returns:
            velocity (np.array): Local/universal velocity vector.
        """
        if local == True: # Convert universal velocity to local velocity
            R = referenceFrames2rotationMatrix(self.universalRF, self.parentRF) # Transform from universalRF to parentRF
            velocity = np.dot(R, self.getVelocity() - self.parent.getVelocity())
        else:
            velocity = np.array([self.state[0], self.state[1], self.state[2]])
        return velocity

    def setVelocity(self, velocity, local=None):
        """
        Set current velocity vector.
        [u, v, w]

        Args:
            velocity (list): Velocity vector to set.
            local (bool): If true velocity is relative to parentRF. Else
                          velocity is relative to universalRF.
        """
        if local == True: # Convert local velocity to universal velocity
            R = referenceFrames2rotationMatrix(self.parentRF, self.universalRF) # Transform from parentRF to universalRF
            velocity = np.dot(R, velocity) + self.parent.getVelocity()
        self.state[0:3] = velocity

    def getPosition(self, local=None):
        """
        Get current position vector.
        [x, y, z]

        Args:
            local (bool): If true position is relative to parentRF. Else
                          position is relative to universalRF.

        Returns:
            position (np.array): Local/universal position vector.
        """
        if local == True: # Convert universal position to local position
            R = referenceFrames2rotationMatrix(self.universalRF, self.parentRF) # Transform from universalRF to parentRF
            position = np.dot(R, self.getPosition() - self.parent.getPosition())
        else:
            position = np.array([self.state[3], self.state[4], self.state[5]])
        return position

    def setPosition(self, position, local=None):
        """
        Set current position vector.
        [x, y, z]

        Args:
            position (list): Position vector to set [x, y, z].
            local (bool): If true position is relative to parentRF. Else
                          position is relative to universalRF.
        """
        if local == True: # Convert local position to universal position
            R = referenceFrames2rotationMatrix(self.parentRF, self.universalRF) # Transform from parentRF to universalRF
            position = np.dot(R, position) + self.parent.getPosition()
        self.state[3:6] = position

    def getAttitudeDot(self, local=None):
        """
        Get current attitude_dot vector.
        [phi_d, theta_d, psi_d]

        Args:
            local (bool): If true attitude_dot is relative to bodyRF. Else
                          attitude_dot is relative to universalRF.

        Returns:
            attitude_dot (np.array): Body/universal attitude_dot vector.
        """
        if local == True: # Convert universal attitude_dot to local (bodyRF) attitude_dot
            R = referenceFrames2rotationMatrix(self.universalRF, self.bodyRF) # Transform from universalRF to bodyRF
            attitude_dot = np.dot(R, self.getAttitudeDot())
        else:
            attitude_dot = np.array([self.state[6], self.state[7], self.state[8]])
        return attitude_dot

    def setAttitudeDot(self, attitude_dot, local=None):
        """
        Set current attitude_dot vector.
        [phi_d, theta_d, psi_d]

        Args:
            attitude_dot (list): AttitudeDot vector to set.
            local (bool): If true attitude_dot is relative to bodyRF. Else
                          attitude_dot is relative to universalRF.
        """
        if local == True: # Convert local (bodyRF) attitude_dot to universal attitude_dot
            R = referenceFrames2rotationMatrix(self.bodyRF, self.universalRF) # Transform from bodyRF to universalRF
            attitude_dot = np.dot(R, attitude_dot)
        self.state[6:9] = attitude_dot

    def getAttitude(self, local=None): ### WORKING IN QUATERNIONS ###
        """
        Get current attitude vector.
        [qw, qx, qy, qz]

        Args:
            local (bool): If true attitude is relative to northeastdownRF. Else
                          attitude is relative to universalRF.

        Returns:
            attitude (Quaternion): parentRF/universalRF attitude vector.
        """
        #self.updateNorthEastDownRF()
        if local == True: # Get attitude relative to local (northeastdownRF) attitude ### WORK IN PROGRESS ###
            attitude = self.getAttitude()
            R = referenceFrames2rotationMatrix(self.universalRF, self.parentRF)
            quaternion = Quaternion(matrix=R)
            #attitude = quaternion * quaternion.inverse.rotate(attitude)
            attitude = quaternion.rotate(quaternion * quaternion.inverse.rotate(attitude))
        else:
            attitude = Quaternion(np.array([self.state[9], self.state[10], self.state[11], self.state[12]]))
        return attitude

    def setAttitude(self, attitude, local=None):  ### WORKING IN QUATERNIONS ###
        """
        Set current attitude vector.
        [qw, qx, qy, qz]

        Args:
            attitude (Quaternion): Attitude vector to set.
            local (bool): If true attitude is relative to parentRF. Else
                          attitude is relative to universalRF.
        """
        if local == True: # Convert local (parentRF) attitude to universal attitude ### WORK IN PROGRESS ###
            # Step 1: Update bodyRF
            i, j, k = self.parentRF.getIJK()
            self.bodyRF.setIJK(i, j, k)
            R = referenceFrames2rotationMatrix(self.parentRF, self.universalRF)
            quaternion = Quaternion(matrix=R)
            attitude = quaternion.rotate(attitude) # Rotate attitude vector so it is in universalRF
            self.bodyRF.rotate(attitude) # Rotate bodyRF
            # Step 2: Update attitude state
            R = referenceFrames2rotationMatrix(self.bodyRF, self.universalRF)
            attitude = Quaternion(matrix=R)
        else:
            self.bodyRF = ReferenceFrame()
            self.bodyRF.rotate(attitude)
        self.state[9:13] = list(attitude)

    def getU(self):
        """
        Get current U vector.
        [Fx, Fy, Fz, Mx, My, Mz]

        Returns:
            U (list): Current U vector.
        """
        return self.U

    def setU(self, U):
        """
        Set current U vector.
        [Fx, Fy, Fz, Mx, My, Mz]

        Args:
            U (list): U vector to set.
        """
        self.U = U

    def addForce(self, force, local=None):
        """
        Add force to current U vector.
        [Fx, Fy, Fz]

        Args:
            force (list): Force vector to add.
            local (bool): If true force is transformed from bodyRF to
                          universalRF before it is added to the U vector.
        """
        if local == True:
            R = referenceFrames2rotationMatrix(self.bodyRF, self.universalRF)
            force = np.dot(R, force)
        self.U[0] += force[0]
        self.U[1] += force[1]
        self.U[2] += force[2]

    def addTorque(self, torque, local=None):
        """
        Add force to current U vector.
        [Mx, My, Mz]

        Args:
            torque (list): Torque vector to add.
            local (bool): If true torque is transformed from bodyRF to
                          universalRF before it is added to the U vector.
        """
        if local == True:
            R = referenceFrames2rotationMatrix(self.bodyRF, self.universalRF)
            torque = np.dot(R, torque)
        self.U[3] += torque[0]
        self.U[4] += torque[1]
        self.U[5] += torque[2]
    
    def getParent(self):
        """
        Get parent.

        Returns:
            parent (obj): Typically a CelestialBody object or 'None'.
        """
        return self.parent

    def setParent(self, parent):
        """
        Set parent.

        Args:
            parent (obj): Rigid body representing parent. Typically a CelestialBody object.
        """
        self.parent = parent
    
    def getUniversalRF(self):
        """
        Get RigidBody universal reference frame.

        Returns:
            universalRF (obj): Universal ReferenceFrame object.
        """
        return self.universalRF
    
    def setUniversalRF(self, universalRF):
        """
        Set RigidBody universal reference frame.

        Args:
            universalRF (obj): Universal ReferenceFrame object.
        """
        self.universalRF = universalRF
    
    def getParentRF(self):
        """
        Get RigidBody parent reference frame.

        Returns:
            parentRF (obj): Parent ReferenceFrame object.
        """
        return self.parentRF
    
    def setParentRF(self, parentRF):
        """
        Set RigidBody parent reference frame.

        Args:
            parentRF (obj): Parent ReferenceFrame object.
        """
        self.parentRF = parentRF
    
    def getBodyRF(self):
        """
        Get RigidBody body reference frame.

        Returns:
            bodyRF (obj): Body ReferenceFrame object.
        """
        return self.bodyRF
    
    def setBodyRF(self, bodyRF):
        """
        Set RigidBody body reference frame.

        Args:
            bodyRF (obj): Body ReferenceFrame object.
        """
        self.bodyRF = bodyRF

    def getParentChain(self):
        """
        Get list which describes chain of parent bodies for transforming between
        RFs. Terminates with final bodys RF = None which indicates the universalRF.

        Returns:
            chain (list): List of bodies in chain i.e. the Moons chain would be
                          [Earth, Sun]
        """
        chain = [self.parent]
        while chain[-1] != None:
            chain.append(chain[-1].parent)
        chain = chain[:-1]
        return chain

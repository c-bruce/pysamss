# Date: 06/10/2018
# Author: Callum Bruce
# Python package for simulating space vehicles from launch to orbit. Main module.

from mayavi import mlab
import numpy as np
import copy
from helpermath import *

class ReferenceFrame:
    """
    ReferenceFrame class.
    """
    def __init__(self):
        self.i = np.array([1, 0, 0])
        self.j = np.array([0, 1, 0])
        self.k = np.array([0, 0, 1])

    def rotate(self, quaternion):
        """
        Rotate ReferenceFrame by quaternion.

        Args:
            quaternion (Quaternion): Quaternion to rotate by.
        """
        i = quaternion.rotate(self.i)
        j = quaternion.rotate(self.j)
        k = quaternion.rotate(self.k)
        self.setIJK(i, j, k)

    def rotateAbs(self, quaternion):
        """
        Rotate ReferenceFrame by quaternion. Performs absolute rotation from
        univeralRF.

        Args:
            quaternion (Quaternion): Quaternion to rotate by.
        """
        self.i = np.array([1, 0, 0])
        self.j = np.array([0, 1, 0])
        self.k = np.array([0, 0, 1])
        i = quaternion.rotate(self.i)
        j = quaternion.rotate(self.j)
        k = quaternion.rotate(self.k)
        self.setIJK(i, j, k)

    def getIJK(self):
        """ Get i, j and k vectors. """
        return self.i, self.j, self.k

    def setIJK(self, i, j, k):
        """
        Set i, j and k vectors in universalRF.

        Args:
            i (np.array): Numpy array i vector i.e. np.array([1, 0, 0])
            j (np.array): Numpy array j vector i.e. np.array([0, 1, 0])
            k (np.array): Numpy array k vector i.e. np.array([0, 0, 1])
        """
        self.i = i
        self.j = j
        self.k = k

    def plot(self, figure, origin, scale_factor=None):
        """
        Plot reference frame centered at origin using mayavi.

        Args:
            figure (mlab.figure): Mayavi figure for plot.
            origin (list): Origin of reference frame in universalRF i.e. [x, y, z]
        """
        if scale_factor == None:
            scale_factor = 1
        mlab.quiver3d(origin[0], origin[1], origin[2], self.i[0], self.i[1], self.i[2], scale_factor=scale_factor, color=(1, 0, 0), figure=figure)
        mlab.quiver3d(origin[0], origin[1], origin[2], self.j[0], self.j[1], self.j[2], scale_factor=scale_factor, color=(0, 1, 0), figure=figure)
        mlab.quiver3d(origin[0], origin[1], origin[2], self.k[0], self.k[1], self.k[2], scale_factor=scale_factor, color=(0, 0, 1), figure=figure)

class RigidBody:
    """
    RigidBody class.

    Note:
        - CelestialBody and Vessel classes derive the bulk of their methods
          from RigidBody class.
    """
    def getState(self):
        """
        Get current state vector.
        [u, v, w, x, y, z, phi_d, theta_d, psi_d, w, x, y, z]

        Returns:
            state (list): Current state vector.
        """
        return self.state[-1]

    def setState(self, state):
        """
        Set current state vector.
        [u, v, w, x, y, z, phi_d, theta_d, psi_d, w, x, y, z]

        Args:
            state (list): State vector to set.
        """
        self.state[-1] = state

    def appendState(self, state):
        """
        Append state vector.
        [u, v, w, x, y, z, phi_d, theta_d, psi_d, w, x, y, z]

        Args:
            state (list): State vector to append.
        """
        self.state.append(state)

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
            velocity = np.array([self.state[-1][0], self.state[-1][1], self.state[-1][2]])
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
        self.state[-1][0:3] = velocity

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
            position = np.array([self.state[-1][3], self.state[-1][4], self.state[-1][5]])
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
        self.state[-1][3:6] = position

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
            attitude_dot = np.array([self.state[-1][6], self.state[-1][7], self.state[-1][8]])
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
        self.state[-1][6:9] = attitude_dot

    def getAttitude(self, local=None): ### WORKING IN QUATERNIONS ###
        """
        Get current attitude vector.
        [w, x, y, z]

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
            attitude = Quaternion(np.array([self.state[-1][9], self.state[-1][10], self.state[-1][11], self.state[-1][12]]))
        return attitude

    def setAttitude(self, attitude, local=None):  ### WORKING IN QUATERNIONS ###
        """
        Set current attitude vector.
        [w, x, y, z]

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
        self.state[-1][9:13] = list(attitude)

    def getU(self):
        """
        Get current U vector.
        [Fx, Fy, Fz, Mx, My, Mz]

        Returns:
            U (list): Current U vector.
        """
        return self.U[-1]

    def setU(self, U):
        """
        Set current U vector.
        [Fx, Fy, Fz, Mx, My, Mz]

        Args:
            U (list): U vector to set.
        """
        self.U[-1] = U

    def appendU(self, U):
        """
        Append U vector.
        [Fx, Fy, Fz, Mx, My, Mz]

        Args:
            U (list): U vector to append.
        """
        self.U.append(U)

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
        self.U[-1][0] += force[0]
        self.U[-1][1] += force[1]
        self.U[-1][2] += force[2]

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
        self.U[-1][3] += torque[0]
        self.U[-1][4] += torque[1]
        self.U[-1][5] += torque[2]

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

class CelestialBody(RigidBody):
    """
    CelestialBody class.

    Args:
        mass (float): CelestialBody mass (kg).
        radius (float): CelestialBody radius (m).
        state (list): State vector [u, v, w, x, y, z, phi_d, theta_d, psi_d, phi, theta, psi].
        parent (parent object): Parent object to inherit parentRF from.
    """
    def __init__(self, mass, radius, state=None, parent=None):
        self.mass = mass
        self.I = np.array([[(2 / 5) * mass * radius**2, 0, 0],
                           [0, (2 / 5) * mass * radius**2, 0],
                           [0, 0, (2 / 5) * mass * radius**2]])
        self.radius = radius
        if state == None:
            self.state = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]]
        else:
            self.state = [state]
        self.U = [[0, 0, 0, 0, 0, 0]] # [Fx, Fy, Fz, Mx, My, Mz]
        self.universalRF = ReferenceFrame()
        if parent == None: # If there is no parent the body's parentRF is the univeralRF
            self.parentRF = self.universalRF
            self.bodyRF = copy.copy(self.universalRF)
            self.parent = None
        else: # Else the body's parentRF is the parents bodyRF
            self.parentRF = parent.bodyRF
            self.bodyRF = copy.copy(parent.bodyRF)
            self.parent = parent

    def getMass(self):
        """ Get mass. """
        return self.mass

    def getI(self):
        """ Get inertia matrix I. """
        return self.I

    def getRadius(self):
        """ Get radius. """
        return self.radius

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

class Vessel(RigidBody):
    """
    Vessel class.

    Args:
        stages (list): List of stages [stage1, stage2, ...].
        state (list): State vector [u, v, w, x, y, z, phi_d, theta_d, psi_d, w, x, y, z].
        U (list): U vector [Fx, Fy, Fz, Mx, My, Mz].
        parent (parent object): Parent object to inherit parentRF from.
    """
    def __init__(self, stages, state=None, U=None, parent=None):
        self.stages = stages
        if state == None:
            self.state = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]]
        else:
            self.state = [state]
        if U == None:
            self.U = [[0, 0, 0, 0, 0, 0]]
        else:
            self.U = [U]
        self.universalRF = ReferenceFrame()
        if parent == None: # If there is no parent the vessels parentRF is the univeralRF
            self.parentRF = self.universalRF
            self.bodyRF = copy.copy(self.universalRF)
            self.parent = None
        else: # Else the vessels parentRF is the parents bodyRF
            self.parentRF = parent.bodyRF
            self.bodyRF = copy.copy(parent.bodyRF)
            self.parent = parent
        self.northeastdownRF = None #self.getNorthEastDownRF()
        self.mass = self.getMass()
        self.length = self.getLength()
        self.I = self.getI()
        self.CoM = self.getCoM()
        self.CoT = self.getCoT()
        # Initialise vessel position so it is coincident with CoM.
        R = referenceFrames2rotationMatrix(self.bodyRF, self.parentRF)
        position_delta = np.dot(R, self.CoM)
        self.updatePosition(position_delta)

    def getMass(self):
        """
        Get vessel mass.

        Returns:
            mass (float): Vessel mass (kg).
        """
        mass = 0
        for stage in self.stages:
            mass += stage.mass
        return mass

    def updateMass(self, m_dot):
        """
        Update stages[0] wetmass and mass due to fuel burn m_dot.

        Args:
            m_dot (float): Mass delta -ive denotes fuel burnt.
        """
        # Step 1: Update mass, I and CoM.
        self.stages[0].updateMass(m_dot) # Burn fuel m_dot in stages[0]
        self.mass = self.getMass() # Update mass of vessel
        self.I = self.getI(local=True) # Update inertia tensor of vessel
        dCoM = self.getCoM_delta() # Get how much the CoM has moved
        self.CoM = self.getCoM() # Update the CoM
        # Step 2: Update vessel position due to moving CoM.
        R = transformationMatrix(self.bodyRF, self.parentRF) # transformationMatrix bodyRF -> parentRF
        position_delta = np.dot(R, dCoM)
        self.updatePosition(position_delta)

    def getI(self): ### METHOD NEEDS IMPROVING CURRENTLY ASSUMES CoM IS IN CENTRE OF ROCKET ###
        """
        Get inertia matrix I. Always in bodyRF.

        Returns:
            I (np.array): Inertia tensor (kg.m**2).

        Note:
            - Assumes CoM is in the centre of rocket.
            - Assumes all stages are cylindrical, stacked on top of one another
              with constant radius = stages[-1].radius.
        """
        Ix = (1/2) * self.mass * self.stages[-1].radius**2
        Iy = (1/12) * self.mass * (3 * (self.stages[-1].radius**2) + self.length**2)
        Iz = (1/12) * self.mass * (3 * (self.stages[-1].radius**2) + self.length**2)
        I = np.array([[Ix, 0, 0],
                      [0, Iy, 0],
                      [0, 0, Iz]])
        return I

    def getLength(self):
        """
        Get vessel length.

        Returns:
            length (float): Vessel length (m).
        """
        length = 0
        for stage in self.stages:
            length += stage.length
        return length

    def getCoM(self):
        """
        Get vessel CoM.
        [x, y, z]

        Returns:
            CoM (np.array): Vessel CoM in bodyRF relative to most forward point
                            (m).
        """
        mass = 0
        moment = 0
        for stage in self.stages:
            mass += stage.mass
            moment += stage.position * stage.mass
        CoM = moment/mass
        return CoM

    def getCoM_delta(self):
        """
        Get vessel CoM delta.
        [x, y, z]

        Returns:
            dCoM (np.array): Vessel dCoM in bodyRF (m).
        """
        mass = 0.0
        moment = 0.0
        for stage in self.stages:
            mass += stage.mass
            moment = stage.position * stage.mass
        dCoM = moment/self.mass - self.CoM
        return dCoM

    def getCoT(self):
        """
        Get vessel CoT.
        [x, y, z]

        Returns:
            CoT (np.array): Vessel CoT in bodyRF relative to most forward point
                            (m).
        """
        CoT = np.array([-self.getLength(), 0, 0])
        return CoT

    def updatePosition(self, position_delta):
        """
        Update current position state by position_delta (used to move position
        state so that it is coincident with vessel CoM).

        Args:
            position_delta (np.array): Amount to move position state by in
                                       parentRF (m).
        """
        position = self.getPosition(local=True) + position_delta
        self.setPosition(position, local=True)

    def getNorthEastDownRF(self):
        """
        Get current north, east, down reference frame. Used for determining
        attitude.

        Returns:
            northeastdownRF (ReferenceFrame obj): Current north, east, down
                                                  reference frame.
        """
        # Step 1: Get parent position, parent north pole position and vessel position
        parentPosition = self.parent.getPosition()
        parentRadius = self.parent.getRadius()
        parent_k = self.parentRF.k
        parentNorthPolePosition = parentPosition + (parent_k * parentRadius)
        vesselPosition = self.getPosition()
        # Step 2: Get i, j, k vectors for north, east, down reference frame
        vecVesselParent = parentPosition - vesselPosition
        vecVesselParentNorthPole = parentNorthPolePosition - vesselPosition
        k = vecVesselParent # k is the vector joining vesselPosition to parentPosition
        j = np.cross(vecVesselParent, vecVesselParentNorthPole) # j is normal to the three points
        i = np.cross(j, k) # i is normal to j and k and completes i, j, k
        # Step 3: Normalise i, j, k vectors
        i = i / np.linalg.norm(i)
        j = j / np.linalg.norm(j)
        k = k / np.linalg.norm(k)
        # Step 4: Create the north, east, down reference frame
        northeastdownRF = ReferenceFrame()
        northeastdownRF.setIJK(i, j, k)
        return northeastdownRF

    def updateNorthEastDownRF(self):
        """
        Update vessel northeastdownRF attribute with current north, east, down
        reference frame.
        """
        northeastdownRF = self.getNorthEastDownRF()
        self.northeastdownRF = northeastdownRF

    def getAttitude(self, local=None): ### WORKING IN QUATERNIONS ###
        """
        Get current attitude vector.
        [w, x, y, z]

        Args:
            local (bool): If true attitude is relative to northeastdownRF. Else
                          attitude is relative to universalRF.

        Returns:
            attitude (Quaternion): northeastdownRF/universalRF attitude vector.
        """
        self.updateNorthEastDownRF()
        if local == True: # Get attitude relative to local (northeastdownRF) attitude ### WORK IN PROGRESS ###
            attitude = self.getAttitude()
            R = referenceFrames2rotationMatrix(self.universalRF, self.northeastdownRF)
            quaternion = Quaternion(matrix=R)
            #attitude = quaternion * quaternion.inverse.rotate(attitude)
            attitude = quaternion.rotate(quaternion * quaternion.inverse.rotate(attitude))
        else:
            attitude = Quaternion(np.array([self.state[-1][9], self.state[-1][10], self.state[-1][11], self.state[-1][12]]))
        return attitude

    def setAttitude(self, attitude, local=None):  ### WORKING IN QUATERNIONS ###
        """
        Set current attitude vector.
        [w, x, y, z]

        Args:
            attitude (Quaternion): Attitude vector to set.
            local (bool): If true attitude is relative to northeastdownRF. Else
                          attitude is relative to universalRF.
        """
        if local == True: # Convert local (northeastdownRF) attitude to universal attitude ### WORK IN PROGRESS ###
            # Step 1: Update bodyRF
            self.bodyRF = self.getNorthEastDownRF()
            R = referenceFrames2rotationMatrix(self.northeastdownRF, self.universalRF)
            quaternion = Quaternion(matrix=R)
            attitude = quaternion.rotate(attitude) # Rotate attitude vector so it is in universalRF
            self.bodyRF.rotate(attitude) # Rotate bodyRF
            # Step 2: Update attitude state
            R = referenceFrames2rotationMatrix(self.bodyRF, self.universalRF)
            attitude = Quaternion(matrix=R)
        else:
            self.bodyRF = ReferenceFrame()
            self.bodyRF.rotate(attitude)
        self.state[-1][9:13] = list(attitude)

    def initAttitude(self):
        """
        Initialise attitude vector.
        [w, x, y, z]

        Note:
            - Defaults to i = -northeastdownRF.k, j = northeastdownRF.i and
              k = -self.northeastdownRF.j
        """
        # Step 1: Rotate bodyRF
        self.updateNorthEastDownRF()
        i = -self.northeastdownRF.k
        j = self.northeastdownRF.i
        k = -self.northeastdownRF.j
        self.bodyRF.setIJK(i, j, k)
        # Step 2: Update attitude state
        R = referenceFrames2rotationMatrix(self.bodyRF, self.universalRF)
        attitude = Quaternion(matrix=R)
        self.state[-1][9:13] = list(attitude)

    def getHeading(self):
        """
        Get vessel heading.

        Returns:
            heading (float): Heading [direction, pitch] (rad).

        Note:
            - North = 0, East = 1.5708, South = 3.1416, West = 4.7124.
            - Up = 1.5708, Down = -1.5708.
        """
        self.updateNorthEastDownRF()
        bodyi = self.bodyRF.i
        R = referenceFrames2rotationMatrix(self.universalRF, self.northeastdownRF)
        bodyi = np.dot(R, bodyi) # Convert bodyi so it is in northeastdownRF
        nedi = [1, 0, 0]
        nedj = [0, 1, 0]
        nedk = [0, 0, 1]
        '''
        north = np.rad2deg(np.arccos((np.dot([bodyi[0], bodyi[2]], [nedi[0], nedi[2]])) /
                          (np.linalg.norm([bodyi[0], bodyi[2]]) * np.linalg.norm([nedi[0], nedi[2]]))))
        east = np.rad2deg(np.arccos((np.dot([bodyi[1], bodyi[2]], [nedj[1], nedj[2]])) /
                         (np.linalg.norm([bodyi[1], bodyi[2]]) * np.linalg.norm([nedj[1], nedj[2]]))))
        north = 90 - north
        east = 90 - east
        '''
        direction = np.arccos((np.dot([bodyi[0], bodyi[1]], [nedi[0], nedi[1]])) /
                              (np.linalg.norm([bodyi[0], bodyi[1]]) * np.linalg.norm([nedi[0], nedi[1]])))
        if bodyi[1] < 0:
            direction += 180
        pitch = -np.arcsin((np.dot(bodyi, nedk)) / (np.linalg.norm(bodyi) * np.linalg.norm(nedk)))
        heading = [direction, pitch]
        return heading

    def getRollPitchYaw(self): ### WORK IN PROGRESS ###
        """
        Get roll, pitch, yaw
        """
'''
class System:
    """
    System object for simulating full systems of Body and Vehicle objects.

    Args:
        bodies (list): List of bodies in system i.e. [Sun, Earth, Moon].
        vehicles (list): List of vehicles in system i.e. [ISS, Falon9].
    """
    def __init__(self, bodies):
        self.bodies = bodies

    def getForceTorque(self):
        """
        Get forces and torques acting on all bodies and vehicles. Sets U vector
        for all bodies and vehicles.
        """

    def simulate(self, scheme, dt, endtime):
'''

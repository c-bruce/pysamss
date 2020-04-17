# Date: 06/01/2019
# Author: Callum Bruce
# Vessel Class
import numpy as np
import copy
from .rigidbody import RigidBody
from .referenceframe import ReferenceFrame
from .stage import Stage
from ..helpermath.helpermath import *

class Vessel(RigidBody):
    """
    Vessel class.

    Args:
        name (str): Vessel name.
        stages (list): List of stages [stage1, stage2, ...].
        state (np.array): State vector [u, v, w, x, y, z, phi_d, theta_d, psi_d, qw, qx, qy, qz].
        U (np.array): U vector [Fx, Fy, Fz, Mx, My, Mz].
        parent_name (str): Name of parent RigidBody object.
    """
    def __init__(self, name=None, stages=[], state=None, U=None, parent_name=None):
        RigidBody.__init__(self, name=name, state=state, U=U, parent_name=parent_name)
        self.stages = stages
        self.mass = self.getMass()
        self.length = self.getLength()
        self.I = self.calculateI()
        self.CoM = self.getCoM()
        self.CoT = self.getCoT()
        self.northeastdownRF = None
    
    def save(self, group):
        """
        Save Vessel object to .h5 file.

            Args:
                group (h5py group): HDF5 file group to save Vessel object to.
        """
        # Save attributes
        group.attrs.create('name', np.string_(self.name))
        group.create_group('stages')
        i = 0
        for stage in self.stages:
            stage_group = group.create_group('stages/' + str(i))
            stage.save(stage_group)
        group.create_dataset('state', data=self.state)
        group.create_dataset('U', data=self.U)
        if self.parent_name is None:
            group.attrs.create('parent_name', np.string_('None'))
        else:
            group.attrs.create('parent_name', np.string_(self.parent.name))
        group.attrs.create('mass', self.mass)
        group.attrs.create('length', self.length)
        group.create_dataset('I', data=self.I)
        group.create_dataset('CoM', data=self.CoM)
        group.create_dataset('CoT', data=self.CoT)
    
    def load(self, group):
        """
        Load Vessel object from .h5 file.

            Args:
                group (h5py group): HDF5 file group to load Vessel object from.
        """
        # Get data
        self.setName(group.attrs['name'].decode('UTF-8'))
        stages = []
        for stage in group['stages']:
            new_stage = Stage()
            new_stage.load(group['stages'][stage])
            stages.append(new_stage)
        self.setStages(stages)
        self.setState(np.array(group.get('state')))
        self.setU(np.array(group.get('U')))
        parent_name = group.attrs['parent_name'].decode('UTF-8')
        if parent_name == 'None':
            parent_name = None
        self.setParentName(parent_name)
        self.setMass(group.attrs['mass'])
        self.setLength(group.attrs['length'])
        self.setI(np.array(group.get('I')))
        self.setCoM(np.array(group.get('CoM')))
        self.setCoT(np.array(group.get('CoT')))
    
    def getStages(self):
        """
        Get Vessel stages.

        Returns:
            stages (list): List of Stage objects.
        """
        return self.stages
    
    def setStages(self, stages):
        """
        Set Vessel stages.

        Args:
            stages (list): List of Stage objects.
        """
        self.stages = stages

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
        self.I = self.calculateI() # Update inertia tensor of vessel
        dCoM = self.getCoM_delta() # Get how much the CoM has moved
        self.CoM = self.getCoM() # Update the CoM
        # Step 2: Update vessel position due to moving CoM.
        R = referenceFrames2rotationMatrix(self.bodyRF, self.parentRF) # rotationMatrix bodyRF -> parentRF
        position_delta = np.dot(R, dCoM)
        self.updatePosition(position_delta)

    def calculateI(self): ### METHOD NEEDS IMPROVING CURRENTLY ASSUMES CoM IS IN CENTRE OF ROCKET ###
        """
        Calculate inertia matrix I. Always in bodyRF.

        Returns:
            I (np.array): Calculated inertia matrix (kg.m**2).

        Note:
            - Assumes CoM is in the centre of rocket.
            - Assumes all stages are cylindrical, stacked on top of one another
              with constant radius = stages[-1].radius.
        """
        Ix = (1/2) * self.mass * self.stages[-1].radius**2
        Iy = (1/12) * self.mass * (3 * (self.stages[-1].radius**2) + self.length**2)
        Iz = (1/12) * self.mass * (3 * (self.stages[-1].radius**2) + self.length**2)
        I = np.array([[Ix, 0.0, 0.0],
                      [0.0, Iy, 0.0],
                      [0.0, 0.0, Iz]])
        return I

    def getLength(self):
        """
        Get vessel length.

        Returns:
            length (float): Vessel length (m).
        """
        length = 0.0
        for stage in self.stages:
            length += stage.length
        return length
    
    def setLength(self, length):
        """
        Set vessel length.

        Args:
            length (float): Vessel length (m).
        """
        self.length = length

    def getCoM(self):
        """
        Get vessel CoM.
        [x, y, z]

        Returns:
            CoM (np.array): Vessel CoM in bodyRF relative to most forward point (m).
        """
        mass = 0.0
        moment = 0.0
        for stage in self.stages:
            mass += stage.mass
            moment += stage.position * stage.mass
        CoM = moment/mass
        return CoM
    
    def setCoM(self, CoM):
        """
        Set vessel CoM.
        [x, y, z]

        Args:
            CoM (np.array): Vessel CoM in bodyRF relative to most forward point (m).
        """
        self.CoM = CoM

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
            CoT (np.array): Vessel CoT in bodyRF relative to most forward point (m).
        """
        CoT = np.array([-self.getLength(), 0, 0])
        return CoT
    
    def setCoT(self, CoT):
        """
        Set vessel CoT.
        [x, y, z]

        Args:
            CoT (np.array): Vessel CoT in bodyRF relative to most forward point (m).
        """
        self.CoT = CoT
    
    def initPosition(self):
        """
        Initialise vessel position so it is coincident with CoM.
        """
        R = referenceFrames2rotationMatrix(self.bodyRF, self.parentRF)
        position_delta = np.dot(R, self.CoM)
        self.updatePosition(position_delta)

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
    
    def initAttitude(self):
        """
        Initialise attitude vector.
        [qw, qx, qy, qz]

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
        self.state[9:13] = list(attitude)

    def getAttitude(self, local=None): ### WORKING IN QUATERNIONS ###
        """
        Get current attitude vector.
        [qw, qx, qy, qz]

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
        self.state[9:13] = list(attitude)

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

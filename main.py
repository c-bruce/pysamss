# Date: 06/10/2018
# Author: Callum Bruce
# Python package for simulating space vehicles from launch to orbit. Main module.

import numpy as np
from helpermath import transformationMatrix

class ReferenceFrame:
    """
    Create ReferenceFrame object.

    Note:
        - Initial self.i = np.array([1,0])
        - Initial self.j = np.array([0,1])
    """
    def __init__(self):
        self.i = np.array([1,0])
        self.j = np.array([0,1])

    def rotate(self,theta):
        i = np.array([1,0])
        j = np.array([0,1])
        R = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta), np.cos(theta)]])
        self.i = np.dot(R,i)
        self.j = np.dot(R,j)

class ReferenceFrame3D:
    """
    Create ReferenceFrame object.

    Note:
        - Initial self.i = np.array([1, 0, 0])
        - Initial self.j = np.array([0, 1, 0])
        - Initial self.k = np.array([0, 0, 1])
    """
    def __init__(self):
        self.i = np.array([1, 0, 0])
        self.j = np.array([0, 1, 0])
        self.k = np.array([0, 0, 1])

    def rotate(self, phi, theta, psi):
        """
        Rotate ReferenceFrame about x (phi), y (theta) and z (psi).

        Args:
            phi (float): Angle to rotate about in x [rads].
            theta (float): Angle to rotate about in y [rads].
            psi (float): Angle to rotate about in z [rads].
        """
        i = np.array([1, 0, 0])
        j = np.array([0, 1, 0])
        k = np.array([0, 0, 1])

        Rx = np.array([[1, 0, 0],
                       [0, np.cos(phi), -np.sin(phi)],
                       [0, np.sin(phi), np.cos(phi)]])

        Ry = np.array([[np.cos(theta), 0, np.sin(theta)],
                       [0, 1, 0],
                       [-np.sin(theta), 0, np.cos(theta)]])

        Rz = np.array([[np.cos(psi), -np.sin(psi), 0],
                       [np.sin(psi), np.cos(psi), 0],
                       [0, 0, 1]])

        R = np.matmul(Rz,np.matmul(Ry,Rx))
        '''
        R = np.array([[np.cos(psi)*np.cos(theta), np.cos(psi)*np.sin(theta)*np.sin(phi) - np.sin(psi)*np.cos(phi), np.cos(psi)*np.sin(theta)*np.cos(phi) + np.sin(psi)*np.sin(phi)],
                      [np.sin(psi)*np.cos(theta), np.sin(psi)*np.sin(theta)*np.sin(phi) + np.cos(psi)*np.cos(phi), np.sin(psi)*np.sin(theta)*np.cos(phi) - np.cos(psi)*np.sin(phi)],
                      [-np.sin(theta), np.cos(theta)*np.sin(phi), np.cos(theta)*np.cos(phi)]])
        '''
        self.i = np.dot(Rx,i)
        self.j = np.dot(Ry,j)
        self.k = np.dot(Rz,k)

class Body:
    """
    Create Body object

    Args:
        mass (float): Body mass (kg)
        radius (float): Body radius (m)
        state (list): Body state [u, v, w, x, y, z, phi_d, theta_d, psi_d, phi, theta, psi]
        bodyRF (obj): Body referenceFrame
    """
    def __init__(self, mass, radius, state, RF):
        self.mass = mass
        self.radius = radius
        self.state = [state]
        self.U = [] # [Fx, Fy, Fz, Mx, My, Mz] BodyRF
        self.Ix = (2 / 5) * mass * radius**2
        self.Iy = (2 / 5) * mass * radius**2
        self.Iz = (2 / 5) * mass * radius**2
        self.RF = RF

    ### GET METHODS ###
    def getMass(self):
        return self.mass

    def getRadius(self):
        return self.radius

    def getState(self):
        state = self.state[-1]
        return state

    def getU(self):
        U = np.array(self.U[-1])
        return U

    def getIx(self):
        return self.Ix

    def getIy(self):
        return self.Iy

    def getIz(self):
        return self.Iz

    def getRF(self):
        RF = self.RF
        return RF

    def getPosition(self):
        position = np.array([self.state[-1][3], self.state[-1][4], self.state[-1][5]])
        return position

    ### SET METHODS ###
    def setState(self, state):
        self.state[-1] = state

    def setRF(self, RF):
        self.RF = RF

    def appendState(self, state):
        self.state.append(state)

    def appendU(self,U):
        self.U.append(U)

class Stage:
    """
    Create Stage object.

    Args:
        mass (float): Stage mass (kg)
        radius (float): Stage radius (m)
        length (float): Stage length (m)
        position (list): Stage position relative to referenceFrame [x,y] (m)

    Note:
        - Stage objects are assumed cylindrical with CoT 0.5*length aft of position.
        - drymass = 0.05*mass, wetmass = 0.95*mass
    """
    def __init__(self,mass,radius,length,position):
        self.mass = mass
        self.drymass = 0.05*mass
        self.wetmass = 0.95*mass
        self.radius = radius
        self.length = length
        self.position = np.array(position)

class Vehicle:
    """
    Create Vehicle object made up of stage objects.

    Args:
        stages (list): List of stages [stage1,stage2,...]
        state (list): Vehicle state [u,v,x,y,phidot,phi]
        RF (obj): Vehicle body referenceFrame
        parentRF (obj): Vehicle parent referenceFrame
    """
    def __init__(self,stages,state,RF,parentRF):
        self.stages = stages
        self.state = [state]
        self.U = [] # [Fx, Fy, Mz] VehicleRF
        self.RF = RF
        self.parentRF = parentRF
        self.mass = 0.0
        self.length = 0.0
        moment = 0.0
        for stage in stages:
            self.mass += stage.mass
            self.length += stage.length
            moment += stage.position*stage.mass
        self.CoM = moment/self.mass
        self.CoT = np.array([-self.length,0])
        ### Iz METHOD NEEDS IMPROVING CURRENTLY ASSUMES CoM IS IN CENTRE OF ROCKET
        self.Iz = (1/12)*self.mass*(3*(self.stages[-1].radius**2)+self.length**2) # Assumes constant radius = stage[-1].radius
        self.state[-1][0] = self.state[-1][0] + self.CoM[0]
        self.state[-1][1] = self.state[-1][1] + self.CoM[1]

    ### GET METHODS ###
    def getState(self):
        state = np.array(self.state[-1])
        return state

    def getU(self):
        U = np.array(self.U[-1])
        return U

    def getVelocity(self):
        velocity = np.array([self.state[-1][0],self.state[-1][1]])
        return velocity

    def getPosition(self):
        position = np.array([self.state[-1][2],self.state[-1][3]])
        return position

    def getPhiDot(self):
        phidot = np.array([self.state[-1][4]])
        return phidot

    def getPhi(self):
        phi = np.array([self.state[-1][5]])
        return phi

    def getRF(self):
        RF = self.RF
        return RF

    def getMass(self):
        mass = self.mass
        return mass

    def getIz(self):
        Iz = self.Iz
        return Iz

    def getCoM(self):
        CoM = self.CoM
        return CoM

    def getCoT(self):
        CoT = self.CoT
        return CoT

    ### SET METHODS ###
    def setState(self,state):
        self.state[-1] = state

    def setRF(self,RF):
        self.RF = RF

    def rotateRF(self,theta):
        self.RF.rotate(theta)

    def setVelocity(self,velocity):
        self.state[-1][0] = velocity[0]
        self.state[-1][1] = velocity[1]

    def setPosition(self,position):
        self.state[-1][2] = position[0]
        self.state[-1][3] = position[1]

    def setPhiDot(self,phidot):
        self.state[-1][4] = phidot

    def setPhi(self,phi):
        self.state[-1][5] = phi

    def appendState(self,state):
        self.state.append(state)

    def appendU(self,U):
        self.U.append(U)

    ### UPDATE METHODS ###
    def updateMass(self,m_dot):
        """
        Update self.stage[0].wetmass by m_dot.

        Args:
            m_dot (float): Mass delta -ive denotes fuel burnt.
        """
        self.stages[0].wetmass = self.stages[0].wetmass + m_dot
        self.stages[0].mass = self.stages[0].drymass + self.stages[0].wetmass
        self.mass = 0.0
        moment = 0.0
        for stage in self.stages:
            self.mass += stage.mass
            moment = stage.position*stage.mass
        dCoM = moment/self.mass - self.CoM
        self.CoM = moment/self.mass
        ### Iz METHOD NEEDS IMPROVING CURRENTLY ASSUMES CoM IS IN CENTRE OF ROCKET
        self.Iz = (1/12)*self.mass*(3*(self.stages[-1].radius**2)+self.length**2) # Assumes constant radius = stage[-1].radius
        T = transformationMatrix(self.RF,self.parentRF) # transformationMatrix self.RF -> self.parentRF
        position = self.getPosition() + np.dot(T,dCoM)
        self.setPosition(position)

class System:
    """
    System object for simulating full systems of Body and Vehicle objects.

    Args:
        bodies (list): List of bodies with parent-child structure i.e.
                       [Sun, [Earth, Moon]].
        vehicles (list): List of vehicles with parent-child structure same shape
                         as bodies i.e. [nan, [ISS]] or [nan, [nan, CM]]
    """
    def __init__(self, bodies):
        self.bodies = bodies

# Date: 06/10/2018
# Author: Callum Bruce
# Python package for simulating space vehicles from launch to orbit. Main module.

import numpy as np
from helpermath import transformationMatrix

class referenceFrame:
    """
    Create referenceFrame object.
    
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

class body:
    """
    Create body object
    
    Args:
        mass (float): Body mass (kg)
        radius (float): Body radius (m)
        state (list): Body state [u,v,x,y,r,phi]
        bodyRF (obj): Body referenceFrame
    """
    def __init__(self,mass,radius,state,RF):
        self.mass = mass
        self.radius = radius
        self.state = state
        self.RF = RF
        self.Iz = (2 / 5) * mass * radius**2
    
    ### GET METHODS ###
    def getState(self):
        state = self.state
        return state
    
    def getPosition(self):
        position = np.array([self.state[2],self.state[3]])
        return position
    
    def getMass(self):
        mass = self.mass
        return mass
    
    def getIz(self):
        Iz = self.Iz
        return Iz
    
    def getRF(self):
        RF = self.RF
        return RF
    
    ### SET METHODS ###
    def setState(self,state):
        self.state = state
        
    def setRF(self,RF):
        self.RF = RF

class stage:
    """
    Create stage object.
    
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

class vehicle:
    """
    Create vehicle object made up of stage objects.
    
    Args:
        stages (list): List of stages [stage1,stage2,...]
        state (list): Vehicle state [u,v,x,y,phidot,phi]
        RF (obj): Vehicle body referenceFrame
        parentRF (obj): Vehicle parent referenceFrame
    """
    def __init__(self,stages,state,RF,parentRF):
        self.stages = stages
        self.state = state
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
        self.state[0] = self.state[0] + self.CoM[0]
        self.state[1] = self.state[1] + self.CoM[1]
    
    ### GET METHODS ###
    def getState(self):
        state = np.array(self.state)
        return state
    
    def getVelocity(self):
        velocity = np.array([self.state[0],self.state[1]])
        return velocity
    
    def getPosition(self):
        position = np.array([self.state[2],self.state[3]])
        return position
    
    def getPhiDot(self):
        phidot = np.array([self.state[4]])
        return phidot
    
    def getPhi(self):
        phi = np.array([self.state[5]])
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
        self.state = state
    
    def setRF(self,RF):
        self.RF = RF
    
    def rotateRF(self,theta):
        self.RF.rotate(theta)
    
    def setVelocity(self,velocity):
        self.state[0] = velocity[0]
        self.state[1] = velocity[1]
        
    def setPosition(self,position):
        self.state[2] = position[0]
        self.state[3] = position[1]
    
    def setPhiDot(self,phidot):
        self.state[4] = phidot
    
    def setPhi(self,phi):
        self.state[5] = phi
        
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
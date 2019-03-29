# Date: 06/10/2018
# Author: Callum Bruce
# Python package for simulating space vehicles from launch to orbit. Main module.

from mayavi import mlab
import numpy as np
import copy
from helpermath import transformationMatrix3D, rotateVector

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
    ReferenceFrame class.
    """
    def __init__(self):
        self.i = np.array([1, 0, 0])
        self.j = np.array([0, 1, 0])
        self.k = np.array([0, 0, 1])

    def rotate(self, phi, theta, psi):
        """
        Rotate ReferenceFrame about x (phi), y (theta) and z (psi).

        Args:
            phi (float): Angle to rotate about in x (rad).
            theta (float): Angle to rotate about in y (rad).
            psi (float): Angle to rotate about in z (rad).
        """
        i = rotateVector(phi, theta, psi, self.i)
        j = rotateVector(phi, theta, psi, self.j)
        k = rotateVector(phi, theta, psi, self.k)
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

class CelestialBody:
    """
    CelestialBody class.

    Args:
        mass (float): Body mass (kg).
        radius (float): Body radius (m).
        state (list): Body state [u, v, w, x, y, z, phi_d, theta_d, psi_d, phi, theta, psi].
        observerRF (ReferenceFrame3D): Observer reference frame of object.
    """
    def __init__(self, mass, radius, state=None, parent=None):
        self.mass = mass
        self.radius = radius
        if state == None:
            self.state = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        else:
            self.state = [state]
        self.U = [] # [Fx, Fy, Fz, Mx, My, Mz] BodyRF
        self.Ix = (2 / 5) * mass * radius**2
        self.Iy = (2 / 5) * mass * radius**2
        self.Iz = (2 / 5) * mass * radius**2
        if parent == None: # If there is no parent the body's observerRF is the univeralRF
            observerRF = ReferenceFrame3D()
            bodyRF = ReferenceFrame3D()
            bodyRF.rotate(self.getPhi(), self.getTheta(), self.getPsi())
            self.observerRF = observerRF
            self.bodyRF = bodyRF
            self.parent = None
        else: # Else the body's observerRF is the parents bodyRF
            observerRF = copy.copy(parent.getBodyRF())
            bodyRF = copy.copy(parent.getBodyRF())
            bodyRF.rotate(self.getPhi(), self.getTheta(), self.getPsi())
            self.observerRF = observerRF
            self.bodyRF = bodyRF
            self.parent = parent

    def getMass(self):
        return self.mass

    def getIx(self):
        return self.Ix

    def getIy(self):
        return self.Iy

    def getIz(self):
        return self.Iz

    def getRadius(self):
        return self.radius

    def getState(self):
        """ Get current state vector. """
        return self.state[-1]

    def setState(self, state):
        """
        Set current state vector.

        Args:
            state (list): State vector to set.
        """
        self.state[-1] = state

    def appendState(self, state):
        """
        Append state vector.

        Args:
            state (list): State vector to append.
        """
        self.state.append(state)

    def getVelocity(self, local=None):
        """
        Get current velocity vector.

        Args:
            local (bool): If true velocity is relative to parentRF. Else
                          velocity is relative to universalRF.

        Returns:
            velocity (np.array): Local/universal velocity vector.
        """
        if local == True:
            velocity = self.getVelocity() # Velocity in universalRF
            chain = self.getParentChain()
            chain = list(reversed(chain)) # Reverse chain to go from universalRF to localRF
            for i in range(0, len(chain) - 1):
                body1 = chain[i]
                body2 = chain[i+1]
                T = transformationMatrix3D(body1.getBodyRF(), body2.getBodyRF())
                velocity = np.dot(T, velocity - body2.getVelocity(local=True))
        else:
            velocity = np.array([self.state[-1][0], self.state[-1][1], self.state[-1][2]])
        return velocity

    def setVelocity(self, velocity, local=None):
        """
        Set current velocity vector.

        Args:
            velocity (list): Position vector to set.
            local (bool): If true velocity is relative to parentRF. Else
                          velocity is relative to universalRF.
        """
        if local == True: # Convert local velocity to universal velocity
            chain = self.getParentChain()
            for i in range(0, len(chain) - 1):
                body1 = chain[i]
                body2 = chain[i+1]
                T = transformationMatrix3D(body1.getBodyRF(), body2.getBodyRF())
                velocity = np.dot(T, velocity + np.array(body1.getVelocity(local=True))) # Transform velocity from body1RF to body2RF
            self.state[-1][0:3] = velocity
        else:
            self.state[-1][0:3] = velocity

    def getPosition(self, local=None):
        """
        Get current position vector.

        Args:
            local (bool): If true position is relative to parentRF. Else
                          position is relative to universalRF.

        Returns:
            position (np.array): Local/universal position vector.
        """
        if local == True:
            position = self.getPosition() # Position in universalRF
            chain = self.getParentChain()
            chain = list(reversed(chain)) # Reverse chain to go from universalRF to localRF
            for i in range(0, len(chain) - 1):
                body1 = chain[i]
                body2 = chain[i+1]
                T = transformationMatrix3D(body1.getBodyRF(), body2.getBodyRF())
                position = np.dot(T, position - body2.getPosition(local=True))
        else:
            position = np.array([self.state[-1][3], self.state[-1][4], self.state[-1][5]])
        return position

    def setPosition(self, position, local=None):
        """
        Set current position vector.

        Args:
            position (list): Position vector to set.
            local (bool): If true position is relative to parentRF. Else
                          position is relative to universalRF.
        """
        if local == True:
            chain = self.getParentChain() # Go from localRF to universalRF
            for i in range(0, len(chain) - 1):
                body1 = chain[i]
                body2 = chain[i+1]
                T = transformationMatrix3D(body1.getBodyRF(), body2.getBodyRF())
                position = np.dot(T, position) + np.array(body1.getPosition(local=True)) # Transform position from body1RF to body2RF
            self.state[-1][3:5] = position
        else:
            self.state[-1][3:5] = position

    def getPhi_d(self):
        phi_d = self.state[-1][6]
        return phi_d

    def getTheta_d(self):
        theta_d = self.state[-1][7]
        return theta_d

    def getPsi_d(self):
        psi_d = self.state[-1][8]
        return psi_d

    def getPhi(self):
        phi = self.state[-1][9]
        return phi

    def getTheta(self):
        theta = self.state[-1][10]
        return theta

    def getPsi(self):
        psi = self.state[-1][11]
        return psi

    def getU(self):
        U = np.array(self.U[-1])
        return U

    def appendU(self, U):
        """
        Append U vector.

        Args:
            U (list): U vector to append.
        """
        self.U.append(U)

    def getParent(self):
        return self.parent

    def getParentChain(self):
        """
        Get list which describes chain of parent bodies for transforming between
        RFs. Terminates with final bodys RF = None which indicates the universalRF.

        Returns:
            chain (list): List of bodies in chain i.e. the Moons chain would be
                          [Earth, Sun]
        """
        chain = [self.getParent()]
        while chain[-1] != None:
            chain.append(chain[-1].getParent())
        chain = chain[:-1]
        return chain

    def getObserverRF(self):
        return self.observerRF

    def getBodyRF(self):
        return self.bodyRF

    def rotateBodyRF(self, phi, theta, psi):
        """
        Rotate bodyRF about x (phi), y (theta) and z (psi).

        Args:
            phi (float): Angle to rotate about in x (rad).
            theta (float): Angle to rotate about in y (rad).
            psi (float): Angle to rotate about in z (rad).
        """
        self.bodyRF.rotate(phi, theta, psi)

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
        - drymass = 0.05*mass, wetmass = 0.95*mass.
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
        stages (list): List of stages [stage1,stage2,...].
        state (list): Vehicle state [u,v,x,y,phidot,phi].
        RF (obj): Vehicle body referenceFrame.
        parentRF (obj): Vehicle parent referenceFrame.
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

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
        - CelestialBody and Vessel classes derive the majority of their methods from RigidBody class.
    """
    def __init__(self, name=None, state=None, U=None, parent_name=None):
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
    
    def getName(self):
        """
        Get RigidBody name.

        Returns:
            name (str): RigidBody name.
        """
        return self.name
    
    def setName(self, name):
        """
        Set RigidBody name.

        Args:
            name (str): RigidBody name.
        """
        self.name = name
    
    def getParentName(self):
        """
        Get RigidBody parent_name.

        Returns:
            parent_name (str): RigidBody parent name.
        """
        return self.parent_name
    
    def setParentName(self, parent_name):
        """
        Set RigidBody parent_name.

        Returns:
            parent_name (str): RigidBody parent name.
        """
        self.parent_name = parent_name

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
    
    def getStateD(self, state0=None, A=None, B=None, U=None):
        """
        Get state derivative vector.
        [u_d, v_d, w_d, x_d, y_d, z_d, phi_dd, theta_dd, psi_dd, qw_d, qx_d, qy_d, qz_d].

        Args:
            state0 (np.array): State vector at t=0. If state0=None the current state vector is used.
            A (np.array): System matrix A. If A=None the current A matrix is used.
            B (np.array): Control matrix B. If B=None the current B matrix is used.
            U (np.array): Input vector U. If U=None the current U vector is used.
        """
        if state0 is None:
            state0 = self.getState()
        if A is None:
            A = self.getA()
        if B is None:
            B = self.getB()
        if U is None:
            U = self.getU()
        state_d = np.dot(A, state0) + np.dot(B, U)
        return state_d

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
    
    def getA(self, state0=None):
        """
        Get system matrix A. A relates how the current state affects the state change.

        Args:
            state0 (np.array): State vector [u, v, w, x, y, z, phi_d, theta_d, psi_d, qw, qx, qy, qz].
                               If state=None current rigid body state is used.
        
        Returns:
            A (np.array): System matrix A.
        """
        if state0 is None:
            state0 = self.getState()
        A = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # . [u, v, w, x, y, z, phi_d, theta_d, psi_d, qw, qx, qy, qz]
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -0.5 * state0[6], -0.5 * state0[7], -0.5 * state0[8]],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5 * state0[6], 0, 0.5 * state0[8], -0.5 * state0[7]],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5 * state0[7], -0.5 * state0[8], 0, 0.5 * state0[6]],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5 * state0[8], 0.5 * state0[7], -0.5 * state0[6], 0]])
        return A

    def getB(self, m=None, Ii=None):
        """
        Get control matrix B. B determines how the system input affects the state change.

        Args:
            m (float): Mass [kg]. If mass=None current rigid body mass is used.
            Ii (np.array): Inverse inertia matrix. If Ii=None current rigid body inverse inertia matrix is used.
        """
        if m is None:
            m = self.getMass()
        if Ii is None:
            Ii = self.getIi()
        B = np.array([[1/m, 0, 0, 0, 0, 0], # . [Fx, Fy, Fz, Mx, My, Mz]
                      [0, 1/m, 0, 0, 0, 0],
                      [0, 0, 1/m, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0],
                      [0, 0, 0, Ii[0,0], Ii[0,1], Ii[0,2]],
                      [0, 0, 0, Ii[1,0], Ii[1,1], Ii[1,2]],
                      [0, 0, 0, Ii[2,0], Ii[2,1], Ii[2,2]],
                      [0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0]])
        return B

    def getU(self):
        """
        Get input vector U.
        [Fx, Fy, Fz, Mx, My, Mz]

        Returns:
            U (list): Current U vector.
        """
        return self.U

    def setU(self, U):
        """
        Set input vector U.
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
    
    def getMass(self):
        """
        Get mass.

        Returns:
            mass (float): CelestialBody mass.
        """
        return self.mass
    
    def setMass(self, mass):
        """
        Get mass.

        Args:
            mass (float): CelestialBody mass.
        """
        self.mass = mass
    
    def getI(self):
        """
        Get inertia matrix I.

        Returns:
            I (np.array): CelestialBody inertia matrix.
        """
        return self.I
    
    def setI(self, I):
        """
        Set inertia matrix I.

        Args:
            I (np.array): CelestialBody inertia matrix.
        """
        self.I = I
    
    def getIi(self):
        """
        Get inverse inertia matrix Ii.

        Returns:
            Ii (np.array): CelestialBody inverse inertia matrix.
        """
        I = self.getI()
        Ii = np.linalg.inv(I)
        return Ii
    
    ### Integration schemes ###

    def euler(self, dt, state0=None, state_d=None):
        """
        Perform Euler integration.
        See https://en.wikipedia.org/wiki/Euler_method.

        Args:
            state0 (np.array): Initial state vector [u, v, w, x, y, z, phi_d, theta_d, psi_d, phi, theta, psi]. If state0=None the
                               current state vector is used.
            state_d (np.array): State derivative vector [u_d, v_d, w_d, x_d, y_d, z_d, phi_dd, theta_dd, psi_dd, phi_d, theta_d, psi_d].
                                If state_d=None the current state derivative vector is used.
            dt (float): Timestep (s).

        Returns:
            state1 (np.array): Updated state vector after time dt [u, v, w, x, y, z, phi_d, theta_d, psi_d, phi, theta, psi].
        """
        # Setup state0 and state_d
        if state0 is None:
            state0 = self.getState()
        if state_d is None:
            state_d = self.getStateD()
        # Calculate state1
        state1 = state0 + state_d * dt
        return state1
    
    def rk4(self, dt, state0=None, state_d=None):
        """
        Perform Runge-Kutta integration.
        https://en.wikipedia.org/wiki/Runge-Kutta_methods

        Args:
            state0 (np.array): Initial state vector [u, v, w, x, y, z, phi_d, theta_d, psi_d, phi, theta, psi]. If state0=None the
                               current state vector is used.
            state_d (np.array): State derivative vector [u_d, v_d, w_d, x_d, y_d, z_d, phi_dd, theta_dd, psi_dd, phi_d, theta_d, psi_d].
                                If state_d=None the current state derivative vector is used.
            dt (float): Timestep (s).

        Returns:
            state1 (np.array): Updated state vector after time dt [u, v, w, x, y, z, phi_d, theta_d, psi_d, phi, theta, psi].
        """
        # Setup state0 and state_d
        if state0 is None:
            state0 = self.getState()
        if state_d is None:
            state_d = self.getStateD()
        # k1
        k1 = state_d
        # k2
        state_k2 = state0 + (0.5 * dt * k1)
        A = self.getA(state0=state_k2)
        k2 = self.getStateD(state0=state_k2, A=A)
        # k3
        state_k3 = state0 + (0.5 * dt * k2)
        A = self.getA(state0=state_k3)
        k3 = self.getStateD(state0=state_k3, A=A)
        # k4
        state_k4 = state0 + (dt * k3)
        A = self.getA(state0=state_k4)
        k4 = self.getStateD(state0=state_k4, A=A)
        # Calculate state1
        state1 = state0 + ((1 / 6) * (k1 + (2 * k2) + (2 * k3) + k4)) * dt
        return state1

    ### Simulate method ###

    def simulate(self, dt, scheme):
        """
        Simulate using a given integration scheme.

        Args:
            scheme (function): Integration scheme i.e. euler.
            dt (float): Time step.
        """
        # Get new state
        state1 = scheme(dt)
        # Update state and U vectors.
        self.setState(state1)
        self.setU(np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
        self.bodyRF.rotateAbs(Quaternion(state1[9:]))
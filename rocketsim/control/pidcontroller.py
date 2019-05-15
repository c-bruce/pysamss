# Date: 06/01/2019
# Author: Callum Bruce
# PID Controller Class
import numpy as np

class PIDcontroller:
    """
    Create PIDcontroller object.

    Args:
        gains (list): Controller gains [Kp,Ki,Kd]
        lims (list): Limits on controller output [max,min]
        windup (float): Windup value between 0 -> 1 (prevents integral windup if error/SP > windup)
    """
    def __init__(self,gains,lims,windup):
        self.Kp = gains[0] # Proportional gain
        self.Ki = gains[1] # Integral gain
        self.Kd = gains[2] # Differential gain
        self.upperLim = lims[0] # Upper limit of output
        self.lowerLim = lims[1] # Lower limit of output
        self.windup = windup # Windup (value between 0 -> 1)
        self.PV = np.array([]) # Process variable
        self.SP = np.array([]) # Set point
        self.error = np.array([0]) # Error
        self.int = np.array([0]) # Integral of error
        self.output = np.array([]) # Output

    def calculate_output(self,PV,SP,dt):
        """
        Calculate output of PID controller.

        Args:
            PV (double): Process variable
            SP (double): Set point
            dt (float): Timestep

        Returns:
            output (double): Controller output
        """
        self.PV = np.append(self.PV,PV)
        self.SP = np.append(self.SP,SP)
        self.error = np.append(self.error,SP-PV)
        if np.absolute((SP-PV)/SP) > self.windup: # Prevent integral windup
            self.int = np.append(self.int,self.int[-1])
        else:
            self.int = np.append(self.int,self.int[-1] + self.error[-1]*dt)
        Pout = self.Kp*self.error[-1]
        Iout = self.Ki*self.int[-1]
        Dout = self.Kd*((self.error[-1]-self.error[-2])/dt)
        output = Pout + Iout + Dout
        if output > self.upperLim:
            output = self.upperLim
        if output < self.lowerLim:
            output = self.lowerLim
        self.output = np.append(self.output,output)
        return output

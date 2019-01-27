# Date: 06/01/2019
# Author: Callum Bruce
# Math helper module

import numpy as np

def transformationMatrix(referenceFrame1,referenceFrame2):
    """
    Transformation matrix for converting from referenceFrame1 to referenceFrame2
    
    Args:
        referenceFrame1 (object): referenceFrame1 object
        referenceFrame2 (object): referenceFrame2 object
        
    Returns:
        T (np.array): Transformation matrix to convert from referenceFrame1 to referenceFrame2
    """
    i = referenceFrame1.i
    j = referenceFrame1.j
    i_d = referenceFrame2.i
    j_d = referenceFrame2.j
    T = np.array([[np.dot(i,i_d),np.dot(j,i_d)],
                  [np.dot(i,j_d),np.dot(j,j_d)]])
    return T
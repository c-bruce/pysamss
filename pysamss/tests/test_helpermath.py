# Date: 14/01/2023
# Author: Callum Bruce
# ReferenceFrame tests
import numpy as np
from pyquaternion import Quaternion

from pysamss.main.referenceframe import ReferenceFrame
from pysamss.helpermath.helpermath import *

def test_referenceFrames2rotationMatrix():
    ref_frame1 = ReferenceFrame()
    ref_frame2 = ReferenceFrame()
    ref_frame2.setIJK([0, 1, 0], [-1, 0, 0], [0, 0, 1])
    R = referenceFrames2rotationMatrix(ref_frame1, ref_frame2)
    expected_R = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])
    assert np.allclose(R, expected_R)
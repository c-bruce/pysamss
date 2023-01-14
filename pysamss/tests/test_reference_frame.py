# Date: 14/01/2023
# Author: Callum Bruce
# ReferenceFrame tests
import numpy as np
from h5py import File
from pyquaternion import Quaternion

from pysamss.main.referenceframe import ReferenceFrame

class TestReferenceFrame:
    def test_init(self):
        ref_frame = ReferenceFrame("test_frame")
        assert ref_frame.name == "test_frame"
        assert (ref_frame.i == np.array([1, 0, 0])).all()
        assert (ref_frame.j == np.array([0, 1, 0])).all()
        assert (ref_frame.k == np.array([0, 0, 1])).all()

    def test_save_load(self):
        ref_frame = ReferenceFrame("test_frame")
        ref_frame.i = np.array([0, 1, 0])
        ref_frame.j = np.array([1, 0, 0])
        ref_frame.k = np.array([0, 0, 1])
        with File("test.h5", "w") as h5_file:
            ref_frame.save(h5_file.create_group("test_group"))
        with File("test.h5", "r") as h5_file:
            ref_frame_loaded = ReferenceFrame()
            ref_frame_loaded.load(h5_file["test_group"])
        assert ref_frame_loaded.name == "test_frame"
        assert (ref_frame_loaded.i == np.array([0, 1, 0])).all()
        assert (ref_frame_loaded.j == np.array([1, 0, 0])).all()
        assert (ref_frame_loaded.k == np.array([0, 0, 1])).all()

    def test_rotate(self):
        ref_frame = ReferenceFrame()
        quaternion = Quaternion(axis=[0, 0, 1], degrees=90)
        ref_frame.rotate(quaternion)
        i, j, k = ref_frame.getIJK()
        assert np.allclose(i, [0, 1, 0])
        assert np.allclose(j, [-1, 0, 0])
        assert np.allclose(k, [0, 0, 1])
    
    def test_rotate_abs(self):
        ref_frame = ReferenceFrame()
        quaternion = Quaternion(axis=[0, 0, 1], degrees=90)
        ref_frame.rotateAbs(quaternion)
        i, j, k = ref_frame.getIJK()
        assert np.allclose(i, [0, 1, 0])
        assert np.allclose(j, [-1, 0, 0])
        assert np.allclose(k, [0, 0, 1])
    
    def test_get_set_IJK(self):
        ref_frame = ReferenceFrame("test_frame")
        ref_frame.setIJK(np.array([0, 1, 0]), np.array([1, 0, 0]), np.array([0, 0, 1]))
        i, j, k = ref_frame.getIJK()
        assert (i == np.array([0, 1, 0])).all()
        assert (j == np.array([1, 0, 0])).all()
        assert (k == np.array([0, 0, 1])).all()
    
    def test_set_name(self):
        ref_frame = ReferenceFrame()
        ref_frame.setName("test_name")
        assert ref_frame.name == "test_name"

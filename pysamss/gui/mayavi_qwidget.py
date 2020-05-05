# Date: 16/06/2019
# Author: Callum Bruce
# MayaviQWidget Class
from tvtk.api import tvtk
from tvtk.pyface.scene_editor import SceneEditor

from mayavi import mlab
from mayavi.tools.engine_manager import EngineManager
from mayavi.tools.mlab_scene_model import MlabSceneModel
from mayavi.core.ui.mayavi_scene import MayaviScene
from mayavi.core.api import PipelineBase, Source, Engine

from traits.api import HasTraits, Instance, Array
from traitsui.api import View, Item

from pyface.qt import QtGui, QtCore

def plotCylinder(scene, radius, height, center):
    """
    Plot cylinder using mayavi and tvtk.

    Args:
        figure (mlab.figure): Mayavi figure for plot.
        radius (float): Cylinder radius (m).
        height (float): Cylinder height (m).
        center (list): Cylinder center [x, y, z] (m).
    """
    cylinder = tvtk.CylinderSource(radius=radius, height=height, center=[-center[1], center[0], center[2]], resolution=90)
    cylinder_mapper = tvtk.PolyDataMapper(input_connection=cylinder.output_port)
    cylinder_actor = tvtk.Actor(mapper=cylinder_mapper, orientation=[0, 0, -90])
    scene.add_actor(cylinder_actor)

class Visualization(HasTraits):
    """
    Visualization class.

    Notes:
        - tvtk.Actor() objects can be added to self.scene in the normal way.
    """
    scene3d = Instance(MlabSceneModel, ())

    def __init__(self, **traits):
        super(Visualization, self).__init__(**traits)
        mlab.pipeline.scalar_field([[0]], figure=self.scene3d.mayavi_scene) # Weird work around to get self.scene3d.mlab.orientation_axes() working
        self.scene3d.mlab.orientation_axes()

    view = View(Item('scene3d', editor=SceneEditor(scene_class=MayaviScene), height=500, width=500, show_label=False), resizable=True)

class MayaviQWidget(QtGui.QWidget):
    """
    MayaviQWidget class.

    Notes:
        - Can be added as a qt widget in the normal way.
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.visualization = Visualization()
        # edit_traits call will generate the widget to embed
        self.ui = self.visualization.edit_traits(parent=self, kind='subpanel').control
        layout.addWidget(self.ui)
        self.ui.setParent(self)

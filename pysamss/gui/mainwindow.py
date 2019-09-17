# Date: 16/06/2019
# Author: Callum Bruce
# MainWindow Class
# Main event loop
from mayavi_qwidget import MayaviQWidget

from tvtk.api import tvtk

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QSplitter, QTreeView, QWidget, QPushButton, QTabWidget

import sys

import numpy as np

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

class MainWindow(QMainWindow):
    """
    MainWindow class.
    """
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("RocketSim")
        layout_top = RibbonWidget()

        layout_middle = MainWidget()
        #print(type(layout_middle.viewer.visualization.scene3d))

        #layout_bottom = QWidget()
        layout_bottom = QHBoxLayout()
        button_plotcylinder = QPushButton("Plot Cylinder")
        button_plotcylinder.pressed.connect(lambda: plotCylinder(layout_middle.viewer.visualization.scene3d, 0.5, 1.0, [np.random.random()*10, np.random.random()*10, np.random.random()*10]))
        layout_bottom.addWidget(button_plotcylinder)
        #layout_bottom.setFixedHeight(100)
        #layout_bottom.addWidget(QPushButton(), 1)

        layout_main = QVBoxLayout()
        layout_main.addWidget(layout_top, 1)
        layout_main.addWidget(layout_middle, 2)
        layout_main.addLayout(layout_bottom, 3)

        widget = QWidget()
        widget.setLayout(layout_main)

        self.setCentralWidget(widget) # Set the central widget of the Window.

class RibbonWidget(QTabWidget):
    """
    RibbonWidget class.

    Classic ribbon sytle File, Tools, View...
    """
    def __init__(self, *args, **kwargs):
        super(RibbonWidget, self).__init__(*args, **kwargs)
        self.setFixedHeight(110)
        # File tab
        self.tab1 = QWidget()
        self.tab1.layout = QHBoxLayout(self)
        self.button_new = QPushButton("New")
        self.button_new.setFixedSize(50, 50)
        self.tab1.layout.addWidget(self.button_new)
        self.button_open = QPushButton("Open")
        self.button_open.setFixedSize(50, 50)
        self.tab1.layout.addWidget(self.button_open)
        self.button_save = QPushButton("Save")
        self.button_save.setFixedSize(50, 50)
        self.tab1.layout.addWidget(self.button_save)
        self.tab1.setLayout(self.tab1.layout)
        self.tab1.layout.setAlignment(Qt.AlignLeft)

        # Tools tab
        self.tab2 = QWidget()
        # View tab
        self.tab3 = QWidget()
        self.addTab(self.tab1, "File")
        self.addTab(self.tab2, "Tools")
        self.addTab(self.tab3, "View")

class MainWidget(QSplitter):
    """
    MainWidget class.

    Main widget containing a QTreeView and MayaviQWidget.
    """
    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)
        self.setOrientation(Qt.Horizontal)
        self.tree = QTreeView()
        self.addWidget(self.tree)
        self.viewer = MayaviQWidget()
        self.addWidget(self.viewer)
        self.setSizes([100, 200])
        #self.setStretchFactor(0, 3)
# Main loop
if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setStyle('Fusion')
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())

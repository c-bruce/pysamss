# Date: 27/04/2019
# Author: Callum Bruce
# MainWindow Class
# Main event loop
from .mayavi_qwidget import MayaviQWidget

from tvtk.api import tvtk

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QSplitter, QTreeView, QWidget, QPushButton, QTabWidget, QSlider

import sys

import numpy as np

from ..helpermath.helpermath import *
'''
def quaternion2euler(quaternion):
    """
    Get Euler angles representation of quaternion [w, x, y, z].

    Args:
        quaternion (list/np.array): Quaternion to convert.

    Returns:
        euler (np.array): Euler angles representation of quaternion.
    """
    w = quaternion[0]
    x = quaternion[1]
    y = quaternion[2]
    z = quaternion[3]
    phi = np.arctan2(2 * ((w * x) + (y * z)), 1 - 2 * (x**2 + y**2))
    theta = np.arcsin(2 * ((w * y) - (z * x)))
    psi = np.arctan2(2 * ((w * z) + (x * y)), 1 - 2 * (y**2 + z**2))
    euler = np.array([phi, theta, psi])
    return euler
'''
class MainWindow(QMainWindow):
    """
    MainWindow class.
    """
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("pySAMSS - Post")
        layout_top = RibbonWidget()

        layout_middle = MainWidget()
        #print(type(layout_middle.viewer.visualization.scene3d))

        #layout_bottom = QWidget()
        #layout_bottom = QHBoxLayout()
        #button_plotcylinder = QPushButton("Plot Cylinder")
        #button_plotcylinder.pressed.connect(lambda: plotCylinder(layout_middle.viewer.visualization.scene3d, 0.5, 1.0, [np.random.random()*10, np.random.random()*10, np.random.random()*10]))
        #layout_bottom.addWidget(button_plotcylinder)
        #layout_bottom.setFixedHeight(100)
        #layout_bottom.addWidget(QPushButton(), 1)

        layout_main = QVBoxLayout()
        layout_main.addWidget(layout_top, 1)
        layout_main.addWidget(layout_middle, 2)

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
        self.setOrientation(Qt.Vertical)
        # Setup MayaviQWidget
        self.viewer = MayaviQWidget()
        self.addWidget(self.viewer)
        # Setup QSlider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFocusPolicy(Qt.StrongFocus)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(10)
        self.slider.setSingleStep(1)
        self.slider.setMaximum(100)
        self.slider.setMinimum(0)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.sliderValueChange)
        self.addWidget(self.slider)
        # Setup system and actors
        self.system = None
        self.actors = {}
    
    def loadSystem(self, system):
        self.system = system
        self.slider.setMaximum(max(list(system.timesteps.keys())))
        timesteps = sorted(list(self.system.timesteps.keys()))
        # CelestialBodies
        for celestial_body in self.system.current.celestial_bodies.values():
            celestial_body_actor = {}
            # Get base actor
            celestial_body_actor['base'] = celestial_body.getActor()
            # Get bodyRF actors
            radius = celestial_body.getRadius()
            position = celestial_body.getPosition()
            i, j, k = celestial_body.bodyRF.getIJK()
            i_points = np.append(np.expand_dims(position, axis=0), np.expand_dims(position + (i * radius * 1.5), axis=0), axis=0)
            j_points = np.append(np.expand_dims(position, axis=0), np.expand_dims(position + (j * radius * 1.5), axis=0), axis=0)
            k_points = np.append(np.expand_dims(position, axis=0), np.expand_dims(position + (k * radius * 1.5), axis=0), axis=0)
            i_source, j_source, k_source, i_actor, j_actor, k_actor = celestial_body.bodyRF.getActors()
            i_source.trait_set(points=i_points)
            j_source.trait_set(points=j_points)
            k_source.trait_set(points=k_points)
            celestial_body_actor['bodyRF'] = [i_points, j_points, k_points, i_source, j_source, k_source, i_actor, j_actor, k_actor]
            # Get trajectory actor
            points = np.empty([len(timesteps), 3])
            for i in range(0, len(timesteps)):
                points[i,:] = system.timesteps[timesteps[i]].celestial_bodies[celestial_body.name].getPosition()
            line_source = tvtk.LineSource(points=points) # Can modify line_source using line_source.trait_set(points=data)
            line_mapper = tvtk.PolyDataMapper(input_connection=line_source.output_port)
            p = tvtk.Property(line_width=2, color=(1, 1, 1))
            line_actor = tvtk.Actor(mapper=line_mapper, property=p)
            celestial_body_actor['trajectory'] = [points, line_source, line_actor]
            # Add actors to the scene
            self.actors[celestial_body.name] = celestial_body_actor
            self.viewer.visualization.scene3d.add_actor(self.actors[celestial_body.name]['base'])
            self.viewer.visualization.scene3d.add_actor(self.actors[celestial_body.name]['bodyRF'][6])
            self.viewer.visualization.scene3d.add_actor(self.actors[celestial_body.name]['bodyRF'][7])
            self.viewer.visualization.scene3d.add_actor(self.actors[celestial_body.name]['bodyRF'][8])
            self.viewer.visualization.scene3d.add_actor(self.actors[celestial_body.name]['trajectory'][2])

    def sliderValueChange(self):
        value = self.slider.value()
        if self.system is not None:
            for celestial_body in self.system.current.celestial_bodies.values():
                # Update base actor
                position = self.system.timesteps[value].celestial_bodies[celestial_body.name].getPosition()
                orientation = np.rad2deg(quaternion2euler(self.system.timesteps[value].celestial_bodies[celestial_body.name].getAttitude()))
                self.actors[celestial_body.name]['base'].trait_set(position=position, orientation=(orientation + np.array([0, 0, 180])))
                # Update bodyRF actors
                radius = self.system.timesteps[value].celestial_bodies[celestial_body.name].getRadius()
                position = self.system.timesteps[value].celestial_bodies[celestial_body.name].getPosition()
                i, j, k = self.system.timesteps[value].celestial_bodies[celestial_body.name].bodyRF.getIJK()
                i_points = np.append(np.expand_dims(position, axis=0), np.expand_dims(position + (i * radius * 1.5), axis=0), axis=0)
                j_points = np.append(np.expand_dims(position, axis=0), np.expand_dims(position + (j * radius * 1.5), axis=0), axis=0)
                k_points = np.append(np.expand_dims(position, axis=0), np.expand_dims(position + (k * radius * 1.5), axis=0), axis=0)
                self.actors[celestial_body.name]['bodyRF'][3].trait_set(points=i_points)
                self.actors[celestial_body.name]['bodyRF'][4].trait_set(points=j_points)
                self.actors[celestial_body.name]['bodyRF'][5].trait_set(points=k_points)
                # Update trajectory actor
                self.actors[celestial_body.name]['trajectory'][1].trait_set(points=self.actors[celestial_body.name]['trajectory'][0][:value + 1])
        self.viewer.visualization.scene3d.render()

# Main loop
if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setStyle('Fusion')
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())

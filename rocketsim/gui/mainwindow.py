# Date: 16/06/2019
# Author: Callum Bruce
# MainWindow Class
# Main event loop
from mayavi_qwidget import MayaviQWidget

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QSplitter, QTreeView, QWidget, QPushButton, QTabWidget

import sys

class MainWindow(QMainWindow):
    """
    MainWindow class.
    """
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("RocketSim")

        layout_top = QHBoxLayout()
        layout_top.addWidget(QPushButton("Button 1"), 1)
        layout_top.addWidget(QPushButton("Button 2"), 2)

        layout_middle = MiddleWidget()
        '''
        layout_middle = QSplitter()
        layout_middle.setOrientation(Qt.Horizontal)
        layout_middle.addWidget(QTreeView())
        layout_middle.addWidget(MayaviQWidget())
        '''
        layout_bottom = QHBoxLayout()
        layout_bottom.addWidget(QPushButton(), 1)

        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_top, 1)
        layout_main.addWidget(layout_middle, 2)
        layout_main.addLayout(layout_bottom, 3)

        widget = QWidget()
        widget.setLayout(layout_main)

        self.setCentralWidget(widget) # Set the central widget of the Window.

class MiddleWidget(QSplitter):
    def __init__(self, *args, **kwargs):
        super(MiddleWidget, self).__init__(*args, **kwargs)
        self.setOrientation(Qt.Horizontal)
        self.addWidget(QTreeView())
        self.addWidget(MayaviQWidget())
# Main loop
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())

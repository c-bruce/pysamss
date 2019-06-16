# Date: 16/06/2019
# Author: Callum Bruce
# MainWindow Class
# Main event loop
from mayavi_qwidget import MayaviQWidget

from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget

import sys

class MainWindow(QMainWindow):
    """
    MainWindow class.
    """
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("RocketSim")

        layout = QVBoxLayout()
        layout.addWidget(MayaviQWidget())

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget) # Set the central widget of the Window.

app = QApplication(sys.argv) # You need one (and only one) QApplication instance per application.

window = MainWindow()
window.show() # Windows are hidden by default.

# Start the event loop.
app.exec_()

###############################################################################
#
#
# Based on code by:
#   Chris Zurbrigg
#
###############################################################################

from PySide import QtCore
from PySide import QtGui

from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

class GUI(QtGui.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(GUI, self).__init__(parent)

        self.setWindowTitle("Test")
        self.setWindowFlags(QtCore.Qt.Tool)

        # Delete UI on close to avoid winEvent error
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.create_layout()
        self.create_connections()

    def create_layout(self):
        self.test_btn = QtGui.QPushButton("Test")

        main_layout = QtGui.QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.addWidget(self.test_btn)

        main_layout.addStretch()

        self.setLayout(main_layout)

    def create_connections(self):
        self.test_btn.clicked.connect(self.testIt)

    def testIt(cls):
        cmds.polyCube()


if __name__ == "__main__":

    # Development workaround for winEvent error when running
    # the script multiple times
    try:
        ui.close()
    except:
        pass

    ui = GUI()
    ui.show()

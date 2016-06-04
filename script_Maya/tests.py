###############################################################################
# Name: 
#   primitives_ui.py
#
# Description: 
#   PySide example that creates a simple GUI for generating 
#   polygon primitives in Maya 2014
#
#   Source code for "A More Practical PySide Example" (http://zurbrigg.com)
#
# Author: 
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
        
        self.setWindowTitle("Primitives")
        self.setWindowFlags(QtCore.Qt.Tool)
        
        # Delete UI on close to avoid winEvent error
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.create_layout()
        self.create_connections()
        
    def create_layout(self):
        self.cube_btn = QtGui.QPushButton("Cube")
        self.sphere_btn = QtGui.QPushButton("Sphere")
        self.cone_btn = QtGui.QPushButton("Cone")
        self.cylinder_btn = QtGui.QPushButton("Cylinder")
        
        main_layout = QtGui.QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.addWidget(self.cube_btn)
        main_layout.addWidget(self.sphere_btn)
        main_layout.addWidget(self.cone_btn)
        main_layout.addWidget(self.cylinder_btn)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
    def create_connections(self):
        self.cube_btn.clicked.connect(PrimitiveUi.make_cube)
        self.sphere_btn.clicked.connect(PrimitiveUi.make_sphere)
        self.cone_btn.clicked.connect(PrimitiveUi.make_cone)
        self.cylinder_btn.clicked.connect(PrimitiveUi.make_cylinder)
        
    @classmethod
    def make_cube(cls):
        cmds.polyCube()
        
    @classmethod
    def make_sphere(cls):
        cmds.polySphere()
        
    @classmethod
    def make_cone(cls):
        cmds.polyCone()
        
    @classmethod
    def make_cylinder(cls):
        cmds.polyCylinder()
        
        
if __name__ == "__main__":
    
    # Development workaround for winEvent error when running
    # the script multiple times
    try:
        ui.close()
    except:
        pass
    
    ui = GUI()
    ui.show()
    
    
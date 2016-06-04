__author__ = 'Paweł Kowalski'
#
# This script was created to demonstrate the use of Python in Autodesk Maya
#
# Copyright (C) Paweł Kowalski
# www.pkowalski.com
# www.behance.net/pkowalski
#
# Open the script from 3D Studio Max Listener with command:
# python.ExecuteFile "path`to`file\main.py"
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#
#

from PySide import QtCore
from PySide import QtGui
from PySide.QtCore import SIGNAL

from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

class DataTable:
    """
    Object stores the parameters of currently running instance of script. It also runs the functions
    and makes callbacks to UI elements easier.
    """

    target_list = None
    target_label = None
    scores_list = []
    current_step = 0  # current step (when running the script step-by-step)
    max_step = 0  # the step that should be performed next (when running the script step-by-step)
    ignore_steps = False  # if ignore_steps is false the animation is step by step

    def __init__(self):
        pass

    def run(self, text, function, path=None):
        """
        Run the script: create the scene. It can run step-by-step and stop after every part or run every function
        one after another. The function also measures an execution time of commands and updates the UI elements.

        :param text: string - Name of the current step that will be displayed in the UI and scores table.
        :param function: function() - Function that will be run.
        :param path: string - Additional parameter: path that can be passed to the function as parameter:
                              required by some functions.
        """

        if self.ignore_steps or self.current_step == self.max_step:  # Skip steps or check if this is the right moment

            self.target_label.setText(text)  # Update the label of UI
            if path is None:  # If no path was passed as argument, then do not pass this variable to target function
                ts = time.time()  # Start measuring time
                function()  # Execute the function passed as an argument
            else:
                ts = time.time()
                function(path)  # if path was passed then pass it to the target function
            te = time.time()  # Record the ending time of command
            score = [text, te - ts]  # Measure the interval
            self.scores_list.append(score)  # append the
            self.max_step += 1  # Update the next step number (important when running step-by-step)
            self.current_step += 2  # Make sure that the next time function is called current_step !-= max_step

            try:
                self.target_list.addItem(QtGui.QListWidgetItem(str(score)))  # Add measured time to scores list in UI
            except:
                pass
        else:  # If function is running step-by-step and it is not the time for ths action just increment the counter.
            self.current_step += 1

    def save(self):
        """
        Funcrtion saves the execution times of commands to the file.
        """

        i = 0
        scores = []

        while i < self.target_list.count():
            scores.append(self.target_list.item(i).text())
            i += 1

        path = QtGui.QFileDialog.getExistingDirectory(None, 'Wybierz folder do zapisu pliku wyniki.txt',
                                                      'D:/Dane/Projekty/licencjat/')
        with open(path + '/wyniki_3DSMax.txt', 'w') as file_:
            for score in scores:
                file_.write(score + '\n')

    def reset(self):
        """
        Function resets the max file and parameters of this object to the initial state.
        """

        self.max_step = 0
        MaxPlus.FileManager.Reset(True)
        MaxPlus.ViewportManager.ForceCompleteRedraw()  # This and the next functions should be run after running the
        MaxPlus.ViewportManager.EnableSceneRedraw()  # script or the viewports will not update.
        pass

class GUI(QtGui.QDialog):

    path = "C:/"

    def __init__(self):

        #set maya main window as parent or it will disappear quickly:
        main_window_ptr = omui.MQtUtil.mainWindow()
        mayaMainWindow = wrapInstance(long(main_window_ptr), QtGui.QWidget)

        super(GUI, self).__init__(mayaMainWindow) # Initialize with mayaMainWindow as a parent

        self.resize(250, 150)  # Set the size of window
        self.center()
        self.setWindowTitle('Skrypt - 3Ds Max')  # Set the title of window
        self.setWindowFlags(QtCore.Qt.Tool) #  The tool window will always be kept on top of parent (maya_main_window)
        
        # Delete UI on close to avoid winEvent error
        #self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        grid = QtGui.QGridLayout()  # Create a grid layout
        grid_internal = QtGui.QGridLayout()
        self.label_info = QtGui.QLabel('Uruchom skrypt wciskajac `start`')  # Create a label GUI element
        btn_step = QtGui.QPushButton('Krok po kroku')  # Create a button
        btn_start = QtGui.QPushButton('Wszystkie kroki')
        self.connect(btn_start, SIGNAL("clicked()"), self.fn_no_steps)  # Connect button to function
        self.connect(btn_step, SIGNAL("clicked()"), self.fn_step)
        self.times_list = QtGui.QListWidget(self)  # Create a list widget
        btn_save = QtGui.QPushButton('Zapisz wyniki')
        btn_reset = QtGui.QPushButton('Wyczysc scene')

        grid.addWidget(self.label_info, 0, 0)  # Add the widget to the layout

        grid_internal.addWidget(btn_step, 0, 0)
        grid_internal.addWidget(btn_start, 0, 1)

        grid.addLayout(grid_internal, 1, 0)
        grid.addWidget(self.times_list, 2, 0)
        grid.addWidget(btn_save, 3, 0)
        grid.addWidget(btn_reset, 4, 0)

        self.data_table = DataTable()
        self.data_table.target_list = self.times_list
        self.data_table.target_label = self.label_info

        self.connect(btn_reset, SIGNAL("clicked()"), self.data_table.reset)
        self.connect(btn_save, SIGNAL("clicked()"), self.data_table.save)

        self.setLayout(grid)  # Set the layout of the window

    def center(self):
        """
        Function places window on the center of the screen. It is not neccesary for script to run.
        """

        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def fn_step(self):
        """
        Run function step-by-step: make one step.
        """

        self.data_table.ignore_steps = False
        self.fn_start()

    def fn_no_steps(self):
        """
        Run function: make all the steps.
        """

        self.data_table.ignore_steps = True
        self.fn_start()

    def fn_start(self):
        """
        Function runs other functions in a right order and with right parameters.
        """

        MaxPlus.ViewportManager.DisableSceneRedraw()  # Makes the script run faster: Viewports will not be updated.

        while not os.path.isfile(self.path + '/land.obj'):  # checks if the folder includes necessary file.
            # If not, then shows the QFileDialog that makes it possible to select the right one.

            self.path = QtGui.QFileDialog.getExistingDirectory(self, 'Wybierz folder z dodatkowymi plikami',
                                                               'D:/Dane/Projekty/licencjat/')
            print self.path

        self.data_table.current_step = 0  # Important when running step-by-step
        self.label_info.setText("Rozpoczeto dzialanie skryptu")
        self.data_table.run(text="Ustawianie sceny", function=prepare_scene, path=self.path)
        self.data_table.run(text="Importowanie podstawowych obiektow", function=import_and_animate_basic_meshes,
                            path=self.path)
        self.data_table.run(text="Tworzenie pletwy rekina i chmury", function=create_shark_and_cloud)
        self.data_table.run(text="Tworzenie skrzynki za pomoca Macro", function=create_chest)
        self.data_table.run(text="Tworzenie i animowanie drzew", function=create_and_animate_trees)
        self.data_table.run(text="Zmiana hierarhii obiektow, koncowa animacja", function=change_hierarchy_and_animate)
        self.data_table.run(text="Tworzenie i przypisywanie materialow", function=create_and_assign_materials)
        
if __name__ == "__main__":
    
    # Development workaround for winEvent error when running
    # the script multiple times
    try:
        ui.close()
    except:
        pass
    
    ui = GUI()
    ui.show()
    
    
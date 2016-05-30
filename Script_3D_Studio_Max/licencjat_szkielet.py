__author__ = 'kowalsp'
from PySide.QtCore import SIGNAL
from PySide import QtGui, QtCore
import MaxPlus
import time
import os
# python.ExecuteFile "C:\Data\Project\skrypty\SpareTime2016Python\main.py"


FPS = MaxPlus.Core.EvalMAXScript('frameRate').GetInt()
TICKS = 4800 / FPS  # convert internal ticks to frames: 4600 ticks per second


def set_scale_keys(obj, keyframes):
    # (object, [[time1, value1], [time2, value2]...])
    # function need to remember the history of scaling to convert absolute values from the input to relative
    # and use them


    MaxPlus.Animation.SetAnimateButtonState(True)
    current_scale = 1.0
    for keyframe in keyframes:
        scale_value = float(keyframe[0]/100.0)
        print scale_value
        scale = MaxPlus.Point3(scale_value / current_scale, scale_value / current_scale, scale_value / current_scale)
        obj.Scale(scale, int(keyframe[1]))
        current_scale = scale_value/100.0
        pass

    MaxPlus.Animation.SetAnimateButtonState(False)


def prepare_scene():
    #Basic tasks: set framerate, timerange, etc.

    #Set animation time range
    time_range = MaxPlus.Animation.GetAnimRange()
    time_range.SetEnd(260 * TICKS)
    time_range.SetStart(0)
    MaxPlus.Animation.SetRange(time_range)

    #Set tangent type to fast
    MaxPlus.Animation.SetDefaultTangentType(3, 3)

    pass


def import_and_animate_basic_meshes(path):
    MaxPlus.FileManager.Import(path + '\water.obj', True)       #importowanie obiektu wody
    water = MaxPlus.INode.GetINodeByName("water")               #Przypisanie obiektu woda do zmiennej
    set_scale_keys(water, [[0.001, 0 * TICKS], [1, 9 * TICKS]]) #animowanie obiektu wody
    MaxPlus.FileManager.Import(path + '\land.obj', True)
    land = MaxPlus.INode.GetINodeByName("land")
    set_scale_keys(land, [[0.001, 0 * TICKS], [1, 9 * TICKS]])


class DataTable():
    target_list = None
    target_label = None
    scores_list = []
    current_step = 0  # current step
    max_step = 0  # the step that should be performed
    ignore_steps = False  # if ignore_steps is false the animation is step by step

    def run(self, name, function, path=None):
        if self.ignore_steps or self.current_step == self.max_step:

            self.target_label.setText(name)
            if path is None:
                ts = time.time()
                function()
            else:
                ts = time.time()
                function(path)
            te = time.time()
            score = [name, te - ts]
            self.scores_list.append(score)
            self.max_step += 1
            self.current_step += 2  # to make sure that the next time function is called current_step !-= max_step
            try:
                self.target_list.addItem(QtGui.QListWidgetItem(str(score)))
            except:
                pass
        else:
            self.current_step += 1

    def reset(self):
        self.max_step = 0
        self.scores_list = []
        self.target_list.clear()
        MaxPlus.FileManager.Reset(True)
        pass


class Example(QtGui.QWidget):
    path = "C:/"

    def __init__(self):
        super(Example, self).__init__()

        self.resize(250, 150)
        self.center()

        self.setWindowTitle('Skrypt - 3Ds Max')
        #Creating the UI elements
        grid = QtGui.QGridLayout()
        grid_internal = QtGui.QGridLayout()
        self.label_info = QtGui.QLabel(u'Uruchom skrypt wciskając `start`')
        btn_step = QtGui.QPushButton('Krok po kroku')
        btn_start = QtGui.QPushButton('Wszystkie kroki')
        self.connect(btn_start, SIGNAL("clicked()"), self.fn_no_steps)
        self.connect(btn_step, SIGNAL("clicked()"), self.fn_step)
        self.times_list = QtGui.QListWidget(self)
        btn_save = QtGui.QPushButton('Zapisz wyniki')
        btn_reset = QtGui.QPushButton(u'Wyczyść scenę')

        #Placing UI elements in the layout of the window
        grid.addWidget(self.label_info, 0, 0)

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

        self.setLayout(grid)
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    #
    # def alert(self, message):
    #     msgBox = QMessageBox()
    #     msgBox.setText(message)

    def fn_step(self):
        self.data_table.ignore_steps = False
        self.fn_start()

    def fn_no_steps(self):
        self.data_table.ignore_steps = True
        self.fn_start()

    def fn_start(self):
        MaxPlus.ViewportManager.DisableSceneRedraw()

        while not os.path.isfile(self.path + '/water.obj'): #if there is no required file (water.obj) in the directory:
            self.path = QtGui.QFileDialog.getExistingDirectory(self, 'Wybierz folder z dodatkowymi plikami',
                                                               'D:/Dane/Projekty/licencjat/')
            print self.path
            #I assume, that if there is a water.obj then there should be land.obj and cloud.obj also in the directory.

        self.data_table.current_step = 0
        self.label_info.setText(u"Rozpoczęto działanie skryptu")
        #Running steps of the script
        self.data_table.run("Ustawianie sceny", prepare_scene)
        self.data_table.run("Importowanie podstawowych obiektów", import_and_animate_basic_meshes, self.path)
        MaxPlus.ViewportManager.ForceCompleteRedraw()
        MaxPlus.ViewportManager.EnableSceneRedraw()
        pass


def main():
    app = QtGui.QApplication.instance()
    if not app:
        app = QtGui.QApplication([])
    ex = Example()
    try:
        import sys
        print 'goodbye world'
        sys.exit(
            app.exec_())
    except SystemExit:
        pass


if __name__ == '__main__':
    main()

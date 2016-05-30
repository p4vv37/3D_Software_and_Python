__author__ = 'kowalsp'
#python.ExecuteFile "C:\Data\Project\skrypty\SpareTime2016Python\main.py"

from profilehooks import profile
from PySide.QtCore import SIGNAL
from PySide import QtGui, QtCore
import MaxPlus



class Example(QtGui.QWidget):
    def __init__(self):
        super(Example, self).__init__()

        self.resize(250, 150)
        self.center()

        self.setWindowTitle('Skrypt - 3Ds Max')

        grid = QtGui.QGridLayout()
        self.label_info = QtGui.QLabel(u'Uruchom skrypt wciskając `start`')
        btn_start = QtGui.QPushButton('Start')
        self.connect(btn_start, SIGNAL("clicked()"), self.fn_start)
        self.times_list = QtGui.QListWidget(self)
        btn_save = QtGui.QPushButton('Zapisz wyniki')

        grid.addWidget(self.label_info, 0, 0)
        grid.addWidget(btn_start, 1, 0)
        grid.addWidget(self.times_list, 2, 0)
        grid.addWidget(btn_save, 3, 0)

        self.setLayout(grid)
        self.show()

    def center(self):

        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def fn_start(self):
        self.label_info.setText(u"Rozpoczęto działanie skryptu")
        info_item = QtGui.QListWidgetItem('test')
        self.times_list.addItem(info_item)
        pass


def main():

    app = QtGui.QApplication.instance()
    if not app:
        app = QtGui.QApplication([])
    ex = Example()
    try:
        import sys
        print 'goodbye world'
        sys.exit(app.exec_()) # Safe way to leave program at any point and allow objects and resources to be cleaned up.
    # Prevent 3ds Max from reporting a system exit as an error in the listener.
    except SystemExit:
        pass


if __name__ == '__main__':
    main()
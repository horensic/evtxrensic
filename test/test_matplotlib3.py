import sys, os, math
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT
from matplotlib.figure import Figure

class NavigationToolbar( NavigationToolbar2QT ):

    picked=pyqtSignal(int,name='picked')

    def __init__(self, canvas, parent ):
        NavigationToolbar2QT.__init__(self,canvas,parent)
        self.clearButtons=[]
        # Search through existing buttons
        # next use for placement of custom button
        next=None
        for c in self.findChildren(QToolButton):
            if next is None:
                next=c
            # Don't want to see subplots and customize
            if str(c.text()) in ('Subplots','Customize'):
                c.defaultAction().setVisible(False)
                continue
            # Need to keep track of pan and zoom buttons
            # Also grab toggled event to clear checked status of picker button
            if str(c.text()) in ('Pan','Zoom'):
                c.toggled.connect(self.clearPicker)
                self.clearButtons.append(c)
                next=None

        # create custom button
        pm=QPixmap(32,32)
        pm.fill(QApplication.palette().color(QPalette.Normal,QPalette.Button))
        painter=QPainter(pm)
        painter.fillRect(6,6,20,20,Qt.red)
        painter.fillRect(15,3,3,26,Qt.blue)
        painter.fillRect(3,15,26,3,Qt.blue)
        painter.end()
        icon=QIcon(pm)
        picker=QAction("Pick",self)
        picker.setIcon(icon)
        picker.setCheckable(True)
        picker.setToolTip("Pick data point")
        self.picker = picker
        button=QToolButton(self)
        button.setDefaultAction(self.picker)

        # Add it to the toolbar, and connect up event
        self.insertWidget(next.defaultAction(),button)
        picker.toggled.connect(self.pickerToggled)

        # Grab the picked event from the canvas
        canvas.mpl_connect('pick_event',self.canvasPicked)

    def clearPicker( self, checked ):
        if checked:
            self.picker.setChecked(False)

    def pickerToggled(self, checked):
        if checked:
            if self._active == "PAN":
                self.pan()
            elif self._active == "ZOOM":
                self.zoom()
            self.set_message('Reject/use observation')

    def canvasPicked( self, event ):
        if self.picker.isChecked():
            self.picked.emit(event.ind)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.x=[i*0.1 for i in range(30)]
        self.y=[math.sin(x) for x in self.x]
        self.picked=[]
        self.setWindowTitle('Custom toolbar')

        self.frame = QWidget()

        self.fig = Figure((4.0, 4.0))
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setParent(self.frame)

        self.axes = self.fig.add_subplot(111)

        # Create the navigation toolbar, tied to the canvas
        # and link the clicked event
        self.toolbar = NavigationToolbar(self.canvas, self.frame)
        self.toolbar.picked.connect(self.addPoint)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.toolbar)
        self.frame.setLayout(vbox)
        self.setCentralWidget(self.frame)
        self.draw()

    def draw(self):
        while self.axes.lines:
            self.axes.lines[0].remove()
        self.axes.plot(self.x,self.y,'b+',picker=5)
        xp=[self.x[i] for i in self.picked]
        yp=[self.y[i] for i in self.picked]
        self.axes.plot(xp,yp,'rs')
        self.canvas.draw()

    def addPoint(self,index):
        if index in self.picked:
            self.picked.remove(index)
        else:
            self.picked.append(index)
        self.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()
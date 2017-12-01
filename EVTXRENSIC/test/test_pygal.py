import sys
import pygal
#from PySide import QtGui, QtSvg
from PyQt4 import QtGui, QtSvg
from PyQt4 import QtWebKit


class Chart(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Chart, self).__init__(parent)

        chart = pygal.StackedLine(fill=True, interpolate='cubic',
                                  style=pygal.style.DefaultStyle)
                                  # or e.g. DarkSolarizedStyle
        chart.add('A', [1, 3, 5, 16, 13, 3, 7])
        chart.add('B', [5, 2, 3, 2, 5, 7, 17])
        chart.add('C', [6, 10, 9, 7, 3, 1, 0])
        chart.add('D', [2, 3, 5, 9, 12, 9, 5])
        chart.add('E', [7, 4, 2, 1, 2, 10, 0])

        self.renderer = QtWebKit.QWebView()
        self.renderer.setContent(chart.render())

    def paintEvent(self, event):
        if self.renderer is not None:
            painter = QtGui.QPainter(self)
            self.renderer.render(painter)
            return True
        return super(Chart, self).paintEvent(event)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Chart()
    window.show()
    result = app.exec_()
    sys.exit(result)
import sys
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QUrl, QDir
from PyQt4.QtWebKit import QWebView
import plotly
import plotly.graph_objs as go


class Browser(QWebView):

    def __init__(self):
        QWebView.__init__(self)
        self.loadFinished.connect(self._result_available)

    def _result_available(self, ok):
        frame = self.page().mainFrame()

if __name__ == '__main__':

    x1 = [10, 3, 4, 5, 20, 4, 3]

    trace1 = go.Box(x=x1)
    layout = go.Layout(showlegend = True)
    data = [trace1]
    fig = go.Figure(data=data, layout = layout)

    fn = './plot.html'

    path = QDir.current().filePath('plotly-latest.min.js')
    local = QUrl.fromLocalFile(path).toString()

    raw_html = '<html><head><meta charset="utf-8" />'
    raw_html += '<script src="{}"></script></head>'.format(local)
    raw_html += '<body>'
    raw_html += plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
    raw_html += '</body></html>'
    print(raw_html)

    app = QApplication(sys.argv)
    view = Browser()
    view.load(QUrl.fromLocalFile(raw_html))
    view.show()
    sys.exit(app.exec_())
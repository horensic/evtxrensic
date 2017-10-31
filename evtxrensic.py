# -*- coding: utf-8 -*-

import sys
import time
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from evtxrensic_form import *
from EventLog import evtx

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class ParseEvtx(QThread):

    def __init__(self, fp):
        QThread.__init__(self)
        self.fp = fp

    def __del__(self):
        self.wait()

    def run(self):
        self.completed = 0
        with evtx.Evtx(self.fp) as eventLog:
            start_time = time.time()
            for o in eventLog.chunks():
                for r in o.records():
                    # r.read_xml()
                    rv = r.get_xml()
                    recordList = [unicode(rv.recordId), unicode(rv.time), unicode(rv.level),
                        unicode(rv.name), unicode(rv.eventId), unicode(rv.task), "N/A"]
                    self.emit(SIGNAL("parse_record(QStringList)"), recordList)
                self.emit(SIGNAL("parse_chunk()"))
            end_time = time.time()
            print("processing time: ", end_time - start_time)

class Evtxrensic(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionOpen.triggered.connect(self._Open)
        self.ui.actionExit.triggered.connect(self.closeEvent)
        self.ui.splitter_dashboard.setStretchFactor(1, 3)
        self.header = self.ui.tableWidget_listpanel.horizontalHeader()
        self.header.setResizeMode(1, QHeaderView.ResizeToContents)
        self.ui.progressBar.setValue(0)

    def _Open(self):
        evtxPath = QFileDialog.getOpenFileName(caption = "Open", filter = "Windows XML Event Log (*.evtx)")
        if evtxPath is None:
            return
        else:
            if evtxPath == u'':
                return
            self.parse_evtx(evtxPath)

    def parse_evtx(self, fp):
        with evtx.Evtx(fp) as eventLog:
            chunkCount = eventLog.fileHeader.number_of_chunks
        self.ui.progressBar.setMaximum(chunkCount)
        self.ui.progressBar.setValue(0)
        self.get_thread = ParseEvtx(fp)
        self.connect(self.get_thread, SIGNAL("parse_record(QStringList)"), self.parse_record)
        self.connect(self.get_thread, SIGNAL("parse_chunk()"), self.parse_chunk)
        self.get_thread.start()

    def parse_record(self, record):
        self.insert_listpanel(record[0], record[1], record[2],
                              record[3], record[4], record[5], record[6])

    def parse_chunk(self):
        self.ui.progressBar.setValue(self.ui.progressBar.value() + 1)

    def insert_listpanel(self, rn, time, level, es, eid, task, info):
        self.rowPosition = self.ui.tableWidget_listpanel.rowCount()
        self.ui.tableWidget_listpanel.insertRow(self.rowPosition)
        self.ui.tableWidget_listpanel.setItem(self.rowPosition, 0,
                                              QTableWidgetItem(_fromUtf8(rn)))
        self.ui.tableWidget_listpanel.setItem(self.rowPosition, 1,
                                              QTableWidgetItem(_fromUtf8(time)))
        self.ui.tableWidget_listpanel.setItem(self.rowPosition, 2,
                                              QTableWidgetItem(_fromUtf8(level)))
        self.ui.tableWidget_listpanel.setItem(self.rowPosition, 3,
                                              QTableWidgetItem(_fromUtf8(es)))
        self.ui.tableWidget_listpanel.setItem(self.rowPosition, 4,
                                              QTableWidgetItem(_fromUtf8(eid)))
        self.ui.tableWidget_listpanel.setItem(self.rowPosition, 5,
                                              QTableWidgetItem(_fromUtf8(task)))
        self.ui.tableWidget_listpanel.setItem(self.rowPosition, 6,
                                              QTableWidgetItem(_fromUtf8(info)))

    def closeEvent(self, event):
        self.deleteLater()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    evtxrensic = Evtxrensic()
    evtxrensic.show()
    sys.exit(app.exec_())

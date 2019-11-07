# coding:utf-8
import sys
import time
import os
import redis
import pandas as pd
import qdarkstyle
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QWidget, QApplication, QGroupBox, QPushButton, QLabel, QHBoxLayout, \
                             QVBoxLayout, QGridLayout, QLineEdit, QFileDialog, QListView, QProgressBar


class WXForm(QWidget):
    def __init__(self):
        super().__init__()
        self.files = None
        self.initUI()
        self.resize(550, 500)

    def initUI(self):
        self.createGridGroupBox()
        self.createFileListBox()
        self.createButtonBox()
        mainLayout = QVBoxLayout()
        hboxLayout = QHBoxLayout()
        self.setWindowTitle('服务器软件')
        hboxLayout.addWidget(self.gridGroupBox)
        mainLayout.addLayout(hboxLayout)
        mainLayout.addWidget(self.ButtonBox)

        mainLayout.addWidget(self.FileListBox)

        self.setLayout(mainLayout)

    def createButtonBox(self):
        self.ButtonBox = QGroupBox()
        layout = QGridLayout()
        self.select_path = QPushButton('选择文件')
        self.select_path.clicked.connect(self.showDialog)
        self.run_btn = QPushButton('上传')
        self.run_btn.clicked.connect(self.start)
        layout.addWidget(self.select_path, 0, 0, 1, 1)
        layout.addWidget(self.run_btn, 0, 1, 1, 1)
        self.ButtonBox.setLayout(layout)

    def createFileListBox(self):
        self.FileListBox = QGroupBox('上传文件')
        layout = QGridLayout()
        self.file_list = QListView()
        self.cmodel = QStandardItemModel(self.file_list)
        layout.addWidget(self.file_list, 1, 0)
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)
        layout.addWidget(self.pbar, 2, 0)
        self.FileListBox.setLayout(layout)

    def createGridGroupBox(self):
        self.gridGroupBox = QGroupBox('服務器信息')
        layout = QGridLayout()
        address = QLabel('服务器地址')
        self.address = QLineEdit('127.0.0.1:6379')
        key = QLabel('数据库键名')
        self.key = QLineEdit('title_license')
        pwd = QLabel('服务器密码')
        self.pwd = QLineEdit('tongna888')
        self.pwd.setEchoMode(QLineEdit.Password)
        layout.setSpacing(10)
        layout.addWidget(address, 1, 0, 1, 1)
        layout.addWidget(self.address, 1, 1, 1, 1)
        layout.addWidget(key, 3, 0, 1, 1)
        layout.addWidget(self.key, 3, 1, 1, 1)
        layout.addWidget(pwd, 2, 0, 1, 1)
        layout.addWidget(self.pwd, 2, 1, 1, 1)
        layout.setColumnStretch(1, 10)
        self.gridGroupBox.setLayout(layout)

    def showDialog(self):
        self.cmodel.clear()
        self.files = QFileDialog.getOpenFileName(self, '选择文件', '', '*.csv')[0]
        if self.files:
            item = QStandardItem()
            item.setText(self.files)
            self.cmodel.appendRow(item)
            self.file_list.setModel(self.cmodel)
    
    def closeEvent(self, event):
        event.accept()
        try:
            os._exit(5) 
        except Exception as e:
            print(e)

    def start(self):
        host, port = self.address.text().split(':')
        pool = redis.ConnectionPool(host=host, port=port, password=self.pwd.text())
        red = redis.Redis(connection_pool=pool)
        data = pd.read_csv(self.files)
        self.length = len(data)
        step = int(self.length / 100)
        inds = {i for i in range(0, self.length, step)}
        inds.add(self.length-1)
        self.pbar.setRange(0, self.length - 1)
        for index, row in enumerate(data.values):
            if index in inds:
                self.pbar.setValue(index)
                QApplication.processEvents()
            red.sadd(self.key.text(), row[0].strip())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sf = WXForm()
    sf.show()
    sys.exit(app.exec_())

# -*- coding: utf-8 -*-

import sys

import numpy as np
import cv2

from pyzbar.pyzbar import decode
from PIL import Image

from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QGridLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showVideo)
        self.cap = cv2.VideoCapture()

        self.initUI()


    def initUI(self):
        self.mainWidget = QWidget()
        self.mainLayout = QGridLayout()

        self.videoLabel = QLabel(self)
        self.videoLabel.resize(640, 480)

        self.openCameraBtn = QPushButton('打开摄像头', self)
        self.openCameraBtn.toggled[bool].connect(self.openCamera)
        self.openCameraBtn.setCheckable(True)
        self.openCameraBtn.setChecked(False)

        self.cameraNumlabel = QLabel('摄像头编号:')
        self.cameraCombox = QComboBox()
        self.cameraList()

        self.hLayout = QHBoxLayout()
        self.hLayout.addWidget(self.cameraNumlabel)
        self.hLayout.addWidget(self.cameraCombox)
        self.hLayout.addWidget(self.openCameraBtn)
        self.hLayout.addStretch(1)

        self.mainLayout.addLayout(self.hLayout, 0, 0)
        self.mainLayout.addWidget(self.videoLabel, 1, 0)

        self.mainWidget.setLayout(self.mainLayout)
        
        self.setCentralWidget(self.mainWidget)
        self.resize(640, 520)
        self.setWindowTitle('二维码扫描自动录入模拟')
        self.show()


    def cameraList(self):
        maxNum = 5
        count = 0
        cap = cv2.VideoCapture()
        for i in range(maxNum):
            if cap.open(i) == True:
                count += 1
                cap.release()
        for i in range(count):
            self.cameraCombox.addItem(str(i))
        if count > 0:
            self.cameraCombox.setCurrentIndex(0)


    def openCamera(self, state):
        if state:
            self.cap.open(int(self.cameraCombox.currentText()))
            self.timer.start(30)
            self.openCameraBtn.setText('关闭摄像头')
        else:
            self.openCameraBtn.setText('打开摄像头')
            self.cap.release()
            self.timer.stop()


    def showVideo(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.image = image
                height, width, bytesPerComponent = image.shape
                bytesPerLine = bytesPerComponent * width
                qImage = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
                self.videoLabel.setPixmap(QPixmap.fromImage(qImage).scaled(self.videoLabel.width(), self.videoLabel.height()))
                result = self.decodeImage()
                if len(result) and result[0].data != '':
                    self.erwermaData = result[0].data.decode('utf-8')
                    self.showEeweimaData(self.erwermaData)
                    self.openCameraBtn.setText('打开摄像头')
                    self.cap.release()
                    self.timer.stop()                   
            else:
                self.cap.release()
                self.timer.stop()


    def decodeImage(self):
        height, width = self.image.shape[:2]
        grey = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        return decode((grey.tobytes(), width, height))
        # image = cv2.imread('erweima.png', cv2.IMREAD_GRAYSCALE)
        # height, width = image.shape[:2]
        # return decode((image.tobytes(), width, height))        


    def showEeweimaData(self, data):
        data = eval(data)
        pJson = data['plaintiff']
        dJson = data['defendant']
        cJson = data['claims']
        tJson = data['truthAndReason']

        content = ''

        pT = '<h4>原告</h4>'
        pB = '<p>'
        for key,val in pJson.items():
            pB += val + ';'
        pB += '</p><hr/>'
        content += pT + pB

        dT = '<h4>被告</h4>'
        dB = '<p>'
        for key,val in dJson.items():
            dB += val + ';'
        dB += '</p><hr/>'
        content += dT + dB

        cT = '<h4>诉讼请求</h4>'
        cB = '<p>'
        for key, val in cJson.items():
            cB += '<li>' + val + '</li>'
        cB += '</p><hr/>'
        content += cT + cB

        tT = '<h4>事实与理由</h4>'
        tB = '<p>'
        for key, val in tJson.items():
            tB += val + ';'
        tB += '</p>'
        content += tT + tB

        QMessageBox.about(self, '起诉书', content)



def main():
	try:
	    app = QApplication(sys.argv)
	    ex = MainWindow()
	    sys.exit(app.exec_())
	except Exception as e:
		print(str(e))
    # app = QApplication(sys.argv)
    # ex = MainWindow()
    # sys.exit(app.exec_())

if __name__ == '__main__':
    main()
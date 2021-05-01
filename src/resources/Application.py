from PyQt5 import QtGui,QtCore
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
import io
import socket
import struct
import time
import pickle
import zlib


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        HOST=socket.gethostname()
        PORT=5409

        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print('Socket created')

        s.bind((HOST,PORT))
        print('Socket bind complete')
        s.listen(10)
        print('Socket now listening')

        conn,addr=s.accept()

        data = b""
        payload_size = struct.calcsize(">L")
        while True:
            while len(data) < payload_size:
                data += conn.recv(4096)

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]
            while len(data) < msg_size:
                data += conn.recv(4096)
            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            self.change_pixmap_signal.emit(frame)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telekey")
        self.setStyleSheet("background-color: white;")
        

        self.setFixedSize(640, 670)
        self.UiComponents()
        # create the label that holds the image
        self.logo_label = QLabel(self)
        self.logomap = QPixmap('logo2')
        self.logo_label.setPixmap(self.logomap)
        
        self.logo_label.setGeometry(0, 5, 75, 75)

        self.image_label = QLabel(self)
        self.image_label.resize(640, 670)
        # create a text label

        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()


    def UiComponents(self):
        # creating a push button
        button = QPushButton("", self)
        # setting geometry of button
        button.setGeometry(570, 5, 75, 75)
        # adding action to a button
        button.clicked.connect(self.settings)
        button.setIcon(QtGui.QIcon('settings.png'))
        button.setIconSize(QtCore.QSize(75,75))
        button.setStyleSheet("border: 1px;")

    def settings(self):
        self.s = SettingsWindow()
        self.s.show()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
        self.image_label.setGeometry(0, 100, 640, 360)

    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 360, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)


class SettingsWindow(QWidget):                           # <===
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setStyleSheet("background-color: white;")
        self.setFixedSize(750, 552)
        self.logo_label = QLabel(self)
        self.logomap = QPixmap('commands.png')
        logomap1 = self.logomap.scaled(750, 552, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.logo_label.setPixmap(logomap1)
        
        self.logo_label.setGeometry(0, 0, 750, 552)
        self.show()

class ApplicationMain(object):
    def runMain(self):
        app = QApplication(sys.argv)
        a = App()
        a.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    #initialize server socket to send messages to gesture script
    m = ApplicationMain()
    m.runMain()

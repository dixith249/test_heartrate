import cv2
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import time
import threading
from Execution import Process

from cam import cam
from interface import imshow, waitKey

class Communicate(QObject):
    closeApp = pyqtSignal()
    
 
class GUI(QMainWindow, QThread):
    def __init__(self):
        super(GUI,self).__init__()
        self.initUI()
        self.cam = cam()
        self.input = self.cam
        self.dirname = ""
        print("Input: cam")
        self.statusBar.showMessage("Input: cam",5000)
        self.btnOpen.setEnabled(False)
        self.process = Process()
        self.status = False
        self.frame = np.zeros((10,10,3),np.uint8)
        self.bpm = 0
        
    def initUI(self):
        font = QFont()
        font.setPointSize(10)
        self.btnStart = QPushButton("Start", self)
        self.btnStart.move(80,230)
        self.btnStart.setFixedWidth(100)
        self.btnStart.setFixedHeight(25)
        self.btnStart.setFont(font)
        self.btnStart.clicked.connect(self.run)
        self.btnOpen = QPushButton("Open", self)
        self.btnOpen.move(0,720)
        self.btnOpen.setFixedWidth(0)
        self.btnOpen.setFixedHeight(0)
        self.btnOpen.setFont(font)
        self.btnOpen.clicked.connect(self.openFileDialog)
        
        self.cbbInput = QComboBox(self)
        self.cbbInput.addItem("cam")
        self.cbbInput.setCurrentIndex(0)
        self.cbbInput.setFixedWidth(0)
        self.cbbInput.setFixedHeight(0)
        self.cbbInput.move(0,700)
        self.cbbInput.setFont(font)
        self.cbbInput.activated.connect(self.selectInput) 
        #self.image = imshow(images1())       
        self.lblDisplay = QLabel(self)
        #self.lblDisplay.setGeometry(10,10,640,480)
        #self.lblDisplay.setStyleSheet("background-color: #000000")   
        self.lblHR = QLabel(self) #Heart Rate
        self.lblHR.setGeometry(80,250,300,40)
        self.lblHR.setFont(font)
        self.lblHR2 = QLabel(self) #Stable HR
        self.lblHR2.setGeometry(100,270,300,40)
        self.lblHR2.setFont(font)
        self.lblHR2.setText("Heart rate: ")
        self.statusBar = QStatusBar()
        self.statusBar.setFont(font)
        self.setStatusBar(self.statusBar)
        self.c = Communicate()
        self.c.closeApp.connect(self.close)
        self.setGeometry(0,0,300,300)
        self.setWindowTitle("Heart BPM")
        self.show()
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def closeEvent(self, event):
        reply = QMessageBox.question(self,"Message", "Are you sure want to quit",
            QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            event.accept()
            self.input.stop()
            cv2.destroyAllWindows()
        else: 
            event.ignore()
    def selectInput(self):
        self.reset()
        if self.cbbInput.currentIndex() == 0:
            self.input = self.cam
            print("Input: cam")
            self.btnOpen.setEnabled(False)      
    def mousePressEvent(self, event):
        self.c.closeApp.emit()    
    def key_handler(self):
        self.pressed = waitKey(1) & 255  # wait for keypress for 10 ms
        if self.pressed == 27:  # exit program on 'esc'
            print("[INFO] Exiting")
            self.cam.stop()
            sys.exit()
    def openFileDialog(self):

       self.statusBar.showMessage("File name: " + self.dirname,5000)
    
    def reset(self):
        self.process.reset()
        self.lblDisplay.clear()
        self.lblDisplay.setStyleSheet("background-color: #000000")
    @QtCore.pyqtSlot()
    def main_loop(self):
        
        frame = self.input.get_frame()

        self.process.frame_in = frame
        self.process.run()
        
        self.frame = self.process.frame_out #get the frame to show in GUI
        self.bpm = self.process.bpm #get the bpm change over the time
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
        img = QImage(self.frame, self.frame.shape[1], self.frame.shape[0], 
                        self.frame.strides[0], QImage.Format_RGB888)
        self.lblDisplay.setPixmap(QPixmap.fromImage(img))
              
        if self.process.bpms.__len__() >50:
            if(max(self.process.bpms-np.mean(self.process.bpms))<5): #show HR if it is stable -the change is not over 5 bpm- for 3s
                self.lblHR2.setText("Heart Rate: " + str(float("{:.2f}".format(np.mean(self.process.bpms)))) + " bpm")
        self.key_handler()  #if not the GUI cant show anything
    def run(self, input):
        self.reset()
        input = self.input
        self.input.dirname = self.dirname
        if self.status == False:
            self.status = True
            input.start()
            self.btnStart.setText("Stop")
            self.cbbInput.setEnabled(False)
            self.btnOpen.setEnabled(False)
            self.lblHR2.clear()
            
            while self.status == True:
                self.main_loop()
                
               
        elif self.status == True:
            self.status = False
            input.stop()
            self.btnStart.setText("Start")
            self.cbbInput.setEnabled(True)
def images1():
    img = cv2.imread('1.jpg')
    cv2.imshow('image', img)
    cv2.waitKey(10000)

    img = cv2.imread('2.jpg')
    cv2.imshow('image', img)
    cv2.waitKey(10000)

    img = cv2.imread('3.jpg')
    cv2.imshow('image', img)
    cv2.waitKey(10000)

    img = cv2.imread('4.jpg')
    cv2.imshow('image', img)
    cv2.waitKey(10000)

    img = cv2.imread('5.jpg')
    cv2.imshow('image', img)
    cv2.waitKey(10000)
    cv2.destroyWindow()

if __name__ == '__main__': 
    app = QApplication(sys.argv)
    ex = GUI()
    t2 = threading.Thread(target=images1())
    ex.status == True
    t1 = threading.Thread(target=ex.main_loop())
    while True: 
         t1.start()
         t2.start()     
    sys.exit(app.exec_())
    #

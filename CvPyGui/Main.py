import cv2,os
from cv2 import CAP_PVAPI_DECIMATION_2OUTOF16
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QApplication, QFileDialog,QMessageBox)
import threading
import threadpool 
from CvPyGui import ImageCvQtContainer
from CvPyGui.ui import gui
import time
from datetime import datetime
import pygame
import pygame.camera
import pyaudio
#import sounddevice as sd

Ui_MainWindow = gui.Ui_MainWindow

#shot
shotmark1 = 0
shotmark2 = 0
shotmark3 = 0

#更新视图
update1 = 0
update2 = 0
update3 = 0

#相机编号
capnum1 = -1
capnum2 = -1
capnum3 = -1

#全局视频分辨率
vw = 640
vh = 480

#录像状态
stop = 1

# pool = threadpool.ThreadPool(4) 

camera_t1 = -1
camera_t2 = -1
camera_t3 = -1

p1 = None
p2 = None
p3 = None

img_no_camera = cv2.imread('no_camera.jpg', cv2.IMREAD_COLOR)
img_no_voice = cv2.imread('no_voice.jpg', cv2.IMREAD_COLOR)

class MyApp(QMainWindow, Ui_MainWindow, threading.Thread):

    filter_count = 0

    def __init__(self):
        super().__init__()
        threading.Thread.__init__(self)
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.initUI()

    def initUI(self):

        self.original1_image = ImageCvQtContainer.Image(
            'camera1', self.original_frame_lbl)
        self.original2_image = ImageCvQtContainer.Image(
            'camera2', self.processed_frame_lbl)
        self.eye_image = ImageCvQtContainer.Image('eye_camera',self.eye_lbl)
        self.voice_image = ImageCvQtContainer.Image('voice_mic',self.voice_lbl)

        self.setBackground()
        self.createButtons()

    def initfrom(self):
        global update1
        update1 = 0
        global update2
        update2 = 0
        self.maxcap=0;
        testmax = 4;
        global caps
        caps = []
        for i in range(testmax):
            cap = cv2.VideoCapture(i)
            if(cap.isOpened()):
                self.maxcap+=1
                caps.append(cap)
            #cap.release()
        self.selecamera1.clear()
        self.selecamera2.clear()
        self.comboBox_2.clear()

        pygame.init()
        pygame.camera.init()
        cameralist = pygame.camera.list_cameras()

        self.selecamera1.addItems([str(i) for i in cameralist])
        self.selecamera2.addItems([str(i) for i in cameralist])
        self.comboBox_2.addItems([str(i) for i in cameralist])

    def stopfrom(self):
        global update1
        update1 = 0
        global update2
        update2 = 0
        global update3
        update3 = 0


    def loop1(self,index,w=1280,h=720):
        
        cap = cv2.VideoCapture(index)
        # cap = caps[index]
        cap.set(6 ,cv2.VideoWriter_fourcc('M', 'J', 'P', 'G') )
        # cap.set(3,w)
        # cap.set(4,h)
        global capnum1
        capnum1 = index
        
        global update1
        update1 = 1
        global shotmark1
        while (update1 == 1):

            ret, frame = cap.read()
            
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.original1_image.updateImage(frame)
            
            if shotmark1 == 1:
                fn = self.lineEdit.text()
                name = "photo/1_"+fn + "video.jpg"
                if os.path.exists(name):
                    name = "photo/1_"+fn + "video"+str(int(time.time()))+".jpg"
                cv2.imwrite(name, frame)
                shotmark1 = 0
            
        cap.release()
        # cv_img_rgb = np.zeros((700,700,3))
        self.original1_image.updateImage(img_no_camera)

    def selecamera1act(self,index,w=1280,h=720):
        global camera_t1
        if camera_t1 != index:
            global p1
            global update1
            update1 = 0
            if p1 and p1.is_alive():
                p1.join()

            p1=threading.Thread(target=self.loop1,args=(index,w,h))
            p1.setDaemon(True)
            p1.start()
            camera_t1 = index
         # threading.Thread.start_new_thread(loop1,text,w=640,h=480)

    def loop2(self,index,w=1280,h=720):
        cap = cv2.VideoCapture(index)
        # cap = caps[index]
        cap.set(6 ,cv2.VideoWriter_fourcc('M', 'J', 'P', 'G') )
        global capnum2
        capnum2 = index
        # cap.set(3,w)
        # cap.set(4,h)
        global update2
        update2 = 1
        global shotmark2

        while (update2 == 1):
            
            ret, frame = cap.read() 
            if shotmark2 == 1:
                fn = self.lineEdit.text()
                name = "photo/2_"+fn + "video.jpg"
                if os.path.exists(name):
                    name = "photo/2_" + fn + "video"+str(int(time.time()))+".jpg"
                cv2.imwrite(name, frame)
                shotmark2 = 0
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.original2_image.updateImage(frame)
        cap.release()
        # cv_img_rgb = np.zeros((700,700,3))
        self.original2_image.updateImage(img_no_camera)

    def selecamera2act(self,index,w=1280,h=720):
        global camera_t2
        if camera_t2 != index:
            global p2
            global update2
            update2 = 0
            if p2 and p2.is_alive():
                p2.join()

            p2=threading.Thread(target=self.loop2,args=(index,w,h))
            p2.setDaemon(True)
            p2.start()
            camera_t2 = index

    def loop3(self,index,w=1280,h=720):
        cap = cv2.VideoCapture(index)
        # cap = caps[index]
        cap.set(6 ,cv2.VideoWriter_fourcc('M', 'J', 'P', 'G') )
        global capnum3
        capnum3 = index
        # cap.set(3,w)
        # cap.set(4,h)
        global update3
        update3 = 1
        global shotmark3

        while (update3 == 1):
            
            ret, frame = cap.read() 
            if shotmark3 == 1:
                fn = self.lineEdit.text()
                name = "photo/3_"+fn + "video.jpg"
                if os.path.exists(name):
                    name = "photo/3_" + fn + "video"+str(int(time.time()))+".jpg"
                cv2.imwrite(name, frame)
                shotmark3 = 0
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.eye_image.updateImage(frame)
        cap.release()
        # cv_img_rgb = np.zeros((700,700,3))
        self.eye_image.updateImage(img_no_camera)

    def selecamera3act(self,index,w=1280,h=720):
        global camera_t3
        if camera_t3 != index:
            global p3
            global update3
            update3 = 0
            if p3 and p3.is_alive():
                p3.join()

            p3=threading.Thread(target=self.loop3,args=(index,w,h))
            p3.setDaemon(True)
            p3.start()
            camera_t3 = index

    def threadRe(self,text="",w=1280,h=720):
        global stop
        stop = 0
        c = 1
        fn = self.lineEdit.text()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        if capnum1 == capnum2:
            c = 0
        cap1 = cv2.VideoCapture(capnum1)
        cap1.set(6 ,cv2.VideoWriter_fourcc('M', 'J', 'P', 'G') )
        cap1.set(3,w)
        cap1.set(4,h)
        if c != 0:
            cap2 = cv2.VideoCapture(capnum2)
            cap2.set(6 ,cv2.VideoWriter_fourcc('M', 'J', 'P', 'G') )
            cap2.set(3,w)
            cap2.set(4,h)
            # name2 = "video/2_" + fn + "video.avi"
            # if os.path.exists(name2):
            name2 = "video/2_" + fn + "_" + datetime.now().strftime('%Y%m%d%H%M%S') + ".avi"
            out2 = cv2.VideoWriter(name2,fourcc, 20.0, (w,h))
        # name1 = "video/1_" + fn + "video.avi"
        # if os.path.exists(name1):
        name1 = "video/1_" + fn + "_"+ datetime.now().strftime('%Y%m%d%H%M%S') +".avi"

        out1 = cv2.VideoWriter(name1,fourcc, 20.0, (w,h))

        if capnum3 != -1 and capnum3 != capnum1 and capnum3 != capnum1:
            cap3 = cv2.VideoCapture(capnum3)
            cap3.set(6 ,cv2.VideoWriter_fourcc('M', 'J', 'P', 'G') )
            cap3.set(3,w)
            cap3.set(4,h)
            name3 = "video/3_"+fn+"_" + datetime.now().strftime('%Y%m%d%H%M%S') + ".avi"
            out3 = cv2.VideoWriter(name3,fourcc, 20.0, (w,h))

        self.statusbar.showMessage('开始录制...',5000)
        while(stop==0):
            ret1, frame1 = cap1.read()
            out1.write(frame1)
            frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            self.original1_image.updateImage(frame1)

            if c != 0:
                ret2, frame2 = cap2.read()
            # # frame = cv2.flip(frame,0)
                out2.write(frame2)
                frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                self.original2_image.updateImage(frame2)

            if capnum3 != -1 and capnum3 != capnum1 and capnum3 != capnum1:
                ret3, frame3 = cap3.read()
                out3.write(frame3)
                frame3 = cv2.cvtColor(frame3, cv2.COLOR_BGR2RGB)
                self.eye_image.updateImage(frame3)

        cap1.release()
        out1.release()
        if c != 0:
            cap2.release()
            out2.release()
        
        if capnum3 != -1 and capnum3 != capnum1 and capnum3 != capnum1:
            cap3.release()
            out3.release()

    def startRe(self):
        if stop == 1:
            global update1
            update1 = 0
            global update2
            update2 = 0
            global p1
            p1=threading.Thread(target=self.threadRe,args=())
            p1.setDaemon(True)
            p1.start()
            self.statusbar.showMessage('准备录制...',5000)
        

    def endRe(self):
        global stop
        stop = 1

        global p1
        global p2

        self.statusbar.showMessage('结束录制...',5000)

        if p1 and p1.is_alive():
            p1.join()
        
        if camera_t1 != -1:
            p1=threading.Thread(target=self.loop1,args=(camera_t1,1280,720))
            p1.setDaemon(True)
            p1.start()

        if camera_t2 != -1:
            p2=threading.Thread(target=self.loop2,args=(camera_t2,1280,720))
            p2.setDaemon(True)
            p2.start()

        self.statusbar.showMessage('空闲中...',5000)
    
    def shotP(self):
        global shotmark1
        shotmark1 = 1
        global shotmark2
        shotmark2 = 1
        global shotmark3
        shotmark3 = 1

    def about(self):
        QMessageBox.about(self, "多通道音视频采集软件",
                "<p>山东大学健康医疗大数据研究院")



    def createButtons(self):

        self.initButton.clicked.connect(self.initfrom)
        self.pushButton.clicked.connect(self.stopfrom)
        self.selecamera1.activated[int].connect(self.selecamera1act)
        self.selecamera2.activated[int].connect(self.selecamera2act)
        self.comboBox_2.activated[int].connect(self.selecamera3act)
        self.startButton.clicked.connect(self.startRe)
        self.endButton.clicked.connect(self.endRe)
        self.shotButton.clicked.connect(self.shotP)
        self.actionAbout.triggered.connect(self.about)  

        # Checkbox for countours
        # self.countours_check_box.stateChanged.connect(self.calculateOriginal)
        # Button for selecting image
        # self.actionOpen_image.triggered.connect(self.openImage)
        # Buttons for saving images
        # self.actionSave_processed_image.triggered.connect(self.processed_image.saveImage)
        # self.actionSave_original_image.triggered.connect(self.original_image.saveImage)
        # self.actionAbout.clicked.connect(self.about)

    def updateImages(self):
        self.calculateProcessed()
        self.calculateOriginal()

    def setBackground(self):
        #cv_img_rgb = np.zeros((700,700,3))
        cv_img_rgb = img_no_camera
        self.original1_image.updateImage(cv_img_rgb)
        self.original2_image.updateImage(cv_img_rgb)
        self.eye_image.updateImage(cv_img_rgb)
        self.voice_image.updateImage(img_no_voice)



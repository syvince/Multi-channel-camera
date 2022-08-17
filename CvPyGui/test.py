import wave

import cv2, os
from cv2 import CAP_PVAPI_DECIMATION_2OUTOF16
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QApplication, QFileDialog, QMessageBox,QPushButton)
import threading
import threadpool
from CvPyGui import ImageCvQtContainer

from CvPyGui.ui import gui
import time
from datetime import datetime
import pygame
import pygame.camera
import pyaudio
# import sounddevice as sd
Ui_MainWindow = gui.Ui_MainWindow
import json

img_no_camera = cv2.imread('config/image/no_camera.jpg', cv2.IMREAD_COLOR)
img_no_voice = cv2.imread('config/image/no_voice.jpg', cv2.IMREAD_COLOR)
img_voice=cv2.imread('config/image/voice.jpg',cv2.IMREAD_COLOR)

class MyApp(QMainWindow, Ui_MainWindow, threading.Thread):
    filter_count = 0
    def __init__(self,chunk=1024, rate=16000):
        super().__init__()
        threading.Thread.__init__(self)
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.initUI()

        self.hd_camera=-1
        self.voice_index=-1
        self.eye_camera=-1
        self.face_camera=-1

        self.hd_width = 1920
        self.hd_height = 1080
        self.face_width = 1920
        self.eye_width = 1280
        self.face_height = 1080
        self.eye_height = 720

        self.hd_fps = 30.0
        self.face_fps = 10.0
        self.eye_fps = 10.0

        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = rate

        self._win1_running = True
        self._win2_running = True
        self._win3_running = True
        self._voice_get = True
        self._begin = False
        self._frames = []


        self._init_running = True
        self._start_running = True

    def initUI(self):
        self.original1_image = ImageCvQtContainer.Image(
            'camera1', self.original_frame_lbl)
        self.original2_image = ImageCvQtContainer.Image(
            'camera2', self.processed_frame_lbl)
        self.eye_image = ImageCvQtContainer.Image('eye_camera', self.eye_lbl)
        self.voice_image = ImageCvQtContainer.Image('voice_mic', self.voice_lbl)
        self.setBackground()
        self.createButtons()

    def r_json(self):
        #读取配置文件
        with open('config/db.json',encoding='utf-8',mode='r') as rf:
            data = rf.read().encode()
            configuration = json.loads(data)
            print(configuration)
            self.hd_cream_name=configuration['hd_camera_name']
            self.face_camera_name=configuration['face_camera_name']
            self.eye_camera_name=configuration['eye_camera_name']
            self.vocie_name=configuration['voice_name']
            self.hk_voice_name=configuration['hk_voice_name']
            self.bluetooth_voice_name=configuration['bluetooth_voice_name']
            self.save_path=configuration['save_path']
            self.hd_width=configuration['hd_width']
            self.hd_height=configuration['hd_height']
            self.hd_fps=configuration['hd_fps']
            self.face_width=configuration['face_width']
            self.face_height=configuration['face_height']
            self.face_fps=configuration['face_fps']
            self.eye_width=configuration['eye_width']
            self.eye_height=configuration['eye_height']
            self.eye_fps=configuration['eye_fps']

    def initfrom(self):
        if self._init_running:
            self._init_running=False
            pygame.init()
            pygame.camera.init()
            cameralist = pygame.camera.list_cameras()
            print(cameralist)
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            voice_list = []
            for i in range(0, numdevices):
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    voice_list.append(p.get_device_info_by_host_api_device_index(0, i).get('name'))
            print(voice_list)

            try:
                self.r_json()
            except:
                self.statusbar.showMessage('未找到配置文件',5000)
            try:
                self.hd_camera=cameralist.index(self.hd_cream_name)
            except:
                self.hd_camera=-1

            try:
                self.face_camera=cameralist.index(self.face_camera_name)
            except:
                self.face_camera=-1

            try:
                self.eye_camera=cameralist.index(self.eye_camera_name)
            except:
                self.eye_camera=-1

            try:
                if self.hk_voice_name in voice_list:
                    self.voice_index = voice_list.index(self.hk_voice_name)
                else:
                    if self.vocie_name in voice_list and self.bluetooth_voice_name in voice_list:
                        self.voice_index=voice_list.index(self.vocie_name)
                        self.CHANNELS=2
                    elif self.vocie_name in voice_list and self.bluetooth_voice_name not in voice_list:
                        self.voice_index=voice_list.index(self.vocie_name)
                        self.CHANNELS=2
                    elif self.vocie_name not in voice_list and self.bluetooth_voice_name in voice_list:
                        self.voice_index=voice_list.index(self.bluetooth_voice_name)
                    else:
                        self.voice_index = -1
            except:
                self.voice_index=-1

            print(self.hd_camera,'行为设备index')
            print(self.face_camera,'面部设备index')
            print(self.eye_camera,'眼部设备index')
            print(self.voice_index,'音频设备index')

            if os.path.exists(self.save_path) is False:
                os.makedirs(self.save_path)

            if self.hd_camera == -1 and self.face_camera == -1 and self.eye_camera ==-1 and self.voice_index ==-1:
                self.statusbar.showMessage('未检测到任何可用设备', 5000)
            elif self.hd_camera != -1 and self.face_camera == -1 and self.eye_camera ==-1 and self.voice_index ==-1:
                self.statusbar.showMessage('未检测到面部、眼部、音频设备',5000)
            elif self.hd_camera == -1 and self.face_camera != -1 and self.eye_camera ==-1 and self.voice_index ==-1:
                self.statusbar.showMessage('未检测到行为、眼部、音频设备', 5000)
            elif self.hd_camera == -1 and self.face_camera == -1 and self.eye_camera !=-1 and self.voice_index ==-1:
                self.statusbar.showMessage('未检测到行为、面部、音频设备', 5000)
            elif self.hd_camera == -1 and self.face_camera == -1 and self.eye_camera ==-1 and self.voice_index !=-1:
                self.statusbar.showMessage('未检测到行为、面部、眼部设备', 5000)

            elif self.hd_camera != -1 and self.face_camera != -1 and self.eye_camera ==-1 and self.voice_index ==-1:
                self.statusbar.showMessage('未检测到眼部、音频设备', 5000)
            elif self.hd_camera != -1 and self.face_camera == -1 and self.eye_camera !=-1 and self.voice_index ==-1:
                self.statusbar.showMessage('未检测到面部、音频设备', 5000)
            elif self.hd_camera != -1 and self.face_camera == -1 and self.eye_camera ==-1 and self.voice_index !=-1:
                self.statusbar.showMessage('未检测到面部、眼部设备', 5000)
            elif self.hd_camera == -1 and self.face_camera != -1 and self.eye_camera !=-1 and self.voice_index ==-1:
                self.statusbar.showMessage('未检测到行为、音频设备', 5000)
            elif self.hd_camera == -1 and self.face_camera != -1 and self.eye_camera ==-1 and self.voice_index !=-1:
                self.statusbar.showMessage('未检测到行为、眼部设备', 5000)
            elif self.hd_camera == -1 and self.face_camera == -1 and self.eye_camera !=-1 and self.voice_index !=-1:
                self.statusbar.showMessage('未检测到行为、面部设备', 5000)

            elif self.hd_camera != -1 and self.face_camera != -1 and self.eye_camera ==-1 and self.voice_index !=-1:
                self.statusbar.showMessage('未检测到眼部设备', 5000)
            elif self.hd_camera != -1 and self.face_camera == -1 and self.eye_camera !=-1 and self.voice_index !=-1:
                self.statusbar.showMessage('未检测到面部设备', 5000)
            elif self.hd_camera == -1 and self.face_camera != -1 and self.eye_camera !=-1 and self.voice_index !=-1:
                self.statusbar.showMessage('未检测到行为设备', 5000)
            elif self.hd_camera != -1 and self.face_camera != -1 and self.eye_camera !=-1 and self.voice_index ==-1:
                self.statusbar.showMessage('未检测到音频设备', 5000)
            else:
                self.statusbar.showMessage('所有设备准备就绪', 5000)
            self.start()
            self.win_4_upimage()
        else:
            pass


    def start(self):
        threading._start_new_thread(self.win_1,())
        threading._start_new_thread(self.win_2,())
        threading._start_new_thread(self.win_3,())

    def win_1(self):
        if self.hd_camera != -1:
            self._win1_running=True
            self.cap1 = cv2.VideoCapture(self.hd_camera,cv2.CAP_DSHOW)
            self.cap1.set(3,self.hd_width)
            self.cap1.set(4,self.hd_height)
            while self._win1_running:
                ret, frame = self.cap1.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.original1_image.updateImage(frame)
            self.original1_image.updateImage(img_no_camera)
        else:
            self.original1_image.updateImage(img_no_camera)

    def win_2(self):
        if self.face_camera != -1:
            self._win2_running=True
            self.cap2 = cv2.VideoCapture(self.face_camera,cv2.CAP_DSHOW)
            self.cap2.set(3,self.face_width)
            self.cap2.set(4,self.face_height)
            while self._win1_running:
                ret, frame = self.cap2.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.original2_image.updateImage(frame)
            self.original2_image.updateImage(img_no_camera)
        else:
            self.original2_image.updateImage(img_no_camera)

    def win_3(self):
        if self.eye_camera != -1:
            self._win3_running=True
            self.cap3 = cv2.VideoCapture(self.eye_camera,cv2.CAP_DSHOW)
            self.cap3.set(3,self.eye_width)
            self.cap3.set(4,self.eye_width)
            while self._win1_running:
                ret, frame = self.cap3.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.eye_image.updateImage(frame)
            self.eye_image.updateImage(img_no_camera)
        else:
            self.eye_image.updateImage(img_no_camera)

    def save_hd_video(self):
        if self.hd_camera != -1:
            fn = self.lineEdit.text()
            name=self.save_path+"/behavior_" + fn + "_" + datetime.now().strftime('%Y%m%d%H%M%S') + ".avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(name, fourcc, self.hd_fps, (self.hd_width, self.hd_height))
            while self._begin:
                ret,frame=self.cap1.read()
                out.write(frame)

    def save_face_video(self):
        if self.face_camera != -1:
            fn = self.lineEdit.text()
            name=self.save_path+"/face_" + fn + "_" + datetime.now().strftime('%Y%m%d%H%M%S') + ".avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(name, fourcc, self.face_fps, (self.face_width, self.face_height))
            while self._begin:
                ret,frame=self.cap2.read()
                out.write(frame)

    def save_eye_video(self):
        if self.eye_camera != -1:
            fn = self.lineEdit.text()
            name=self.save_path+"/eye_" + fn + "_" + datetime.now().strftime('%Y%m%d%H%M%S') + ".avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(name, fourcc, self.eye_fps, (self.eye_width, self.eye_height))
            while self._begin:
                ret,frame=self.cap3.read()
                out.write(frame)

    def win_4_upimage(self):
        if self.voice_index != -1:
            self.voice_image.updateImage(img_voice)
        else:
            pass

    def win_4(self):
        self._voice_get = True
        #print('win_4 start')
        self._frames=[]
        p=pyaudio.PyAudio()
        stream=p.open(format=self.FORMAT,
                      rate=self.RATE,
                      channels=self.CHANNELS,
                      input=True,
                      frames_per_buffer=self.CHUNK,
                      input_device_index=self.voice_index)
        while self._voice_get:
            data = stream.read(self.CHUNK)
            self._frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def voice_save(self):
        #print('voice_end')
        p=pyaudio.PyAudio()
        fn = self.lineEdit.text()
        name= self.save_path+"/vioce_" + fn + "_" + datetime.now().strftime('%Y%m%d%H%M%S') + ".wav"
        wf=wave.open(name,'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self._frames))
        wf.close()
        print("Saved")

    def startRe(self):
        if self._start_running:
            self._start_running =False
            self._begin = True
            self.statusbar.showMessage('开始录制...')
            threading._start_new_thread(self.save_hd_video, ())
            threading._start_new_thread(self.save_face_video, ())
            threading._start_new_thread(self.save_eye_video, ())
            if self.voice_index != -1:
                threading._start_new_thread(self.win_4, ())
        else:
            pass

    def endRe(self):
        if self._start_running==False:
            self._start_running=True
            self._begin =False
            if self.voice_index != -1:
                self._voice_get = False
                self.voice_save()
                self.statusbar.showMessage('空闲中...', 5000)
        else:
            pass

    def stop(self):
        self._win1_running = False
        self._win2_running = False
        self._win3_running = False
        self._init_running = True
        print('stop','所有通道均已断开')
        self.voice_image.updateImage(img_no_voice)
        self.statusbar.showMessage('所有通道均已断开')
        #self.selecamera1act(index=hd_camera_index)
        #self.selecamera2act(index=hd_camera_index)
        #self.voice_get(index=voice_index)
    def f_p(self):
        self._win1_running = False
        self._win2_running = False
        self._win3_running = False
        self._init_running = True
        self._voice_get = True
        self._begin = False
        print('stop', '所有进程均已中止')
        self.statusbar.showMessage('所有进程均已中止')
        self.voice_image.updateImage(img_no_voice)

    def about(self):
        QMessageBox.about(self, "多通道音视频采集软件",
                          "<p>山东大学健康医疗大数据研究院")

    def updateImages(self):
        self.calculateProcessed()
        self.calculateOriginal()

    def createButtons(self):
        self.initButton.clicked.connect(self.initfrom)
        self.pushButton.clicked.connect(self.stop)
        self.shotButton.clicked.connect(self.f_p)
        # #self.selecamera1.activated[int].connect(self.selecamera1act)
        self.actionAbout.triggered.connect(self.about)
        self.startButton.clicked.connect(self.startRe)
        self.endButton.clicked.connect(self.endRe)

    def setBackground(self):
        # cv_img_rgb = np.zeros((700,700,3))
        cv_img_rgb = img_no_camera
        self.original1_image.updateImage(cv_img_rgb)
        self.original2_image.updateImage(cv_img_rgb)
        self.eye_image.updateImage(cv_img_rgb)
        self.voice_image.updateImage(img_no_voice)

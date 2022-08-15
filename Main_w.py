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

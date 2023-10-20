import os.path

import cv2
import numpy as np
import argparse
import shutil

from PyQt5.QtGui import *
from PyQt5.QtCore import *
import resource
import sys
from capture_thread import Thread
from SettingsWindow import *
import Config
import time
import math
import paramiko
import globalStuff
import openpyxl

frame_rate = 25
TIME_SERIES_LENGTH = int(Config.find('alert_frame_count'))
import serial.tools.list_ports

def get_file_indices(front_path, back_path, Out_folder):
    hostname = '192.168.0.100'
    username = 'rider'
    password = 'Rider2021'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)

    stdin, stdout, stderr = ssh.exec_command('ls ' + front_path)

    filenames_front = stdout.read()
    filenames_front = filenames_front.decode('utf-8')
    filenames_front = filenames_front.split("\n")
    filenames_front = [filename for filename in filenames_front if "False" not in filename]

    stdin, stdout, stderr = ssh.exec_command('ls ' + back_path)

    filenames_back = stdout.read()
    filenames_back = filenames_back.decode('utf-8')
    filenames_back = filenames_back.split("\n")
    filenames_back = [filename for filename in filenames_back if "False" not in filename and "Spot_Marginal" not in filename]

    for root, dirs, files in os.walk(Out_folder):
        for directory in dirs:
            if not os.path.exists(os.path.join(Out_folder, directory)):
                continue
            new_files = os.listdir(os.path.join(Out_folder, directory))
            filenames_front = filenames_front + [str(filename) for filename in new_files
                                                 if "false" not in str(filename).lower() and
                                                 "front" in str(filename).lower()]
            filenames_back = filenames_back + [str(filename) for filename in new_files
                                                if "false" not in str(filename).lower() and
                                                "blind" in str(filename).lower()]
    indices = {'Left_Blind_Spot': 0, 'Right_Blind_Spot': 0, 'Bike_Left_Blind_Spot': 0, 'Bike_Right_Blind_Spot': 0,
               'Left_And_Right_Blind_Spot': 0, 'Bike_Left_And_Right_Blind_Spot': 0, 'Front_Collision': 0,
               'Front_Distance': 0, 'Front_Collision_Truck': 0,
               'Front_Distance_Truck': 0, 'Front_Collision_Bike': 0,
               'Front_Distance_Bike': 0, 'Front_Collision_Bus': 0,
               'Front_Distance_Bus': 0, 'Front_Collision_Traffic': 0,
               'Front_Distance_Traffic': 0, 'Front_Collision_Night': 0}
    for name_type in indices:
        print("getting file index for", name_type)
        if "Blind" in name_type:
            filenames = filenames_back
        else:
            filenames = filenames_front
        filenames = [filename for filename in filenames if filename.startswith(name_type)]
        numbers = [filename[len(name_type) + 1:].lstrip().split("_")[0] for filename in filenames]
        if len(numbers) > 0:
            nums = [int(number) for number in numbers if number.isdigit()]
            if len(nums) > 0:
                indices[name_type] = 1 + max(nums)
    return indices


def is_video_file(x):
    if x.find('mp4') != -1 or x.find('avi') != -1 or x.find('MOV') != -1:
        return True
    return False
class Ui(QtWidgets.QMainWindow):
    def __init__(self):

        # Get a list of all available COM ports
        self.LoadAllMovies = True
        self.filename = ''
        self.video_directory = 'J:/New_Alerts/New'
        self.front_videos_list = ['']
        self.frontHover = False
        self.frontImage = None
        self.FrontFrameNum = -1
        self.FrontStuckCounter = 0
        self.BackStuckCounter = 0
        self.front_directory_done = ""
        self.mouseP = [0, 0]
        self.indices = {}
        super(Ui, self).__init__()

        uic.loadUi('ui/mainwindow.ui', self)
        self.setWindowTitle(f"Rider Dome ADAS")

        self.videoSpeed = 0.25

        # Flag to represent the start/stop of 2 cameras at the same time
        self.isAllStarted = False

        self.isFrontStarted = False
        self.frontCamURL = ""
        self.totFrameCountFront = 0
        self.frontCamThread = Thread(self, 1, self.frontCamURL, self.sliderFront.value(), self.videoSpeed)
        self.frontCamThread.changePixmap.connect(self.setImage)
        self.frontCamThread.finishedSignal.connect(self.finishedThread)

        # Variables for back camera
        self.isBackStarted = False
        self.backCamURL = ""
        self.totFrameCountBack = 0
        self.FrontImageMode = 'Normal'

        self.btnTrueAlert = self.findChild(QtWidgets.QPushButton, 'btnTrueAlert')
        self.btnTrueAlert.clicked.connect(self.OnBtnTrueAlert)
        self.btnFalseAlert = self.findChild(QtWidgets.QPushButton, 'btnFalseAlert')
        self.btnFalseAlert.clicked.connect(self.OnBtnFalseAlert)
        self.btnDouble = self.findChild(QtWidgets.QPushButton, 'btnDouble')
        self.btnDouble.clicked.connect(self.OnBtnDouble)

        self.btnFaulty = self.findChild(QtWidgets.QPushButton, 'btnFaulty')
        self.btnFaulty.clicked.connect(self.OnBtnFaulty)

        self.label = self.findChild(QtWidgets.QLabel, 'AlertLabel')

        self.btnOpenFront = self.findChild(QtWidgets.QPushButton, 'btnOpenFront')
        self.btnOpenFront.clicked.connect(self.OnBtnFrontOpen)
        self.lblFrontCamURL = self.findChild(QtWidgets.QLabel, 'lblFrontCamURL')
        self.btnStartFront = self.findChild(QtWidgets.QPushButton, 'btnStartFront')
        self.btnStartFront.clicked.connect(self.OnbtnStartFront)

        self.btnGoToStartFront = self.findChild(QtWidgets.QPushButton, 'btnGoToStartFront')
        self.btnGoToStartFront.clicked.connect(self.OnRefreshFront)
        self.sliderFront = self.findChild(QtWidgets.QSlider, 'sliderFront')
        self.sliderFront.valueChanged.connect(self.OnSliderChangedFront)
        self.sliderFront.sliderMoved.connect(self.OnSliderMovedFront)
        self.imgFrontBox = self.findChild(QtWidgets.QLabel, 'imgFrontBox')

        self.imgFrontBox.setMouseTracking(True)
        self.imgFrontBox.installEventFilter(self)

        self.btnSetting = self.findChild(QtWidgets.QPushButton, 'btnSetting')
        self.btnSetting.clicked.connect(self.OnSetting)
        self.btnClose = self.findChild(QtWidgets.QPushButton, 'btnClose')
        self.btnClose.clicked.connect(self.exit)

        Config.init()
        # Show the main screen as full screen mode
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint)
        # self.showFullScreen()
        self.showMaximized()
        self.OnAppStart()
        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self.tick)
        self.timer.start()
        #
        # globalStuff.alertThread = rau_new.AlertThread(self)
        # globalStuff.alertThread.start()
        #
        # globalStuff.alertThread.alert(0, "")  # green flash
        #
        # parser = argparse.ArgumentParser()
        # parser.add_argument('--front', help='front video file')
        # parser.add_argument('--rear', help='rear video file')
        # parser.add_argument('--frame', type=int, help='start frame')
        #
        # args = parser.parse_args()
        #
        # if args.front:
        #     self.loadFrontVideoFile(args.front)
        #     if args.frame:
        #         self.seek_front(args.frame)
        #         self.sliderFront.setValue(args.frame)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        elif e.key() == Qt.Key_F1:
            self.toggleGrid()
        elif e.key() == Qt.Key_F2:
            self.toggleOFF()

    # Slot function to set image to picture box in UI
    @pyqtSlot(np.ndarray, int, int, bool)
    def setImage(self, image, camID, cur_frame_num, playback):
        if camID == 1:  # Front Camera
            self.frontImage = image
            if playback:
                self.sliderFront.setValue(cur_frame_num)


    @pyqtSlot(bool, int)
    def finishedThread(self, camID):  # isFinished,
        if camID == 1:
            self.isFrontStarted = False

    def closeEvent(self, event):
        self.exit()

    def OnBtnEraseAlertF(self):
        if self.frontCamThread.last_Alert is None:
            return

    def loadFrontVideoFile(self, filename):
        self.frontCamThread.pause = True
        self.isFrontStarted = False
        if self.frontCamThread.isRunning():
            self.frontCamThread.terminate()

        self.frontCamURL = filename
        self.frontCamThread.camURL = self.frontCamURL

        self.totFrameCountFront = self.frontCamThread.StartNewVideo(self.frontCamURL)

        self.lblFrontCamURL.setText(self.frontCamURL)

        self.sliderFront.setRange(0, self.totFrameCountFront)
        self.sliderFront.setValue(0)
        self.label.setText(self.GetAlertName(self.filename))

        if not self.frontCamThread.isRunning():
            self.frontCamThread.frameStartTime = self.sliderFront.value()
            self.frontCamThread.seekFrame = True
            self.frontCamThread.start()

    @staticmethod
    def is_front_footage(x):
        if x.find("BWD") != -1 or x.lower().find("blindspot") != -1 \
                or x.lower().find("blind") != -1 or x.lower().find("blind_spot") != -1:
            return False
        if (x.lower().find("front") != -1 or x.find('F.MOV') != -1 or x.lower().find('safe.MOV') != -1
            or x.find("FWD") != -1 or x.lower().find("collision") or x.lower().find("distance")) \
                and is_video_file(x):
            return True
        return False
    def OnBtnFaulty(self):
        filename = self.filename
        if len(self.front_videos_list) > 1:
            del (self.front_videos_list[0])
            self.filename = self.front_videos_list[0]
            if os.path.exists(self.filename):
                self.loadFrontVideoFile(self.filename)
                self.start_frontCam(True)
        else:
            self.frontCamThread.captured_video.release()
            self.loadFrontVideoFile("NoMoreFiles.mp4")
        if os.path.exists(filename):
            shutil.copy(filename, os.path.join(self.faulty_directory_done, os.path.basename(filename)))
            os.remove(filename)
        else:
            print("Error: no file")


    def OnBtnDouble(self):
        filename = self.filename
        if len(self.front_videos_list) > 1:
            del (self.front_videos_list[0])
            self.filename = self.front_videos_list[0]
            if os.path.exists(self.filename):
                self.loadFrontVideoFile(self.filename)
                self.start_frontCam(True)
        else:
            self.frontCamThread.captured_video.release()
            self.loadFrontVideoFile("NoMoreFiles.mp4")

        if os.path.exists(filename):
            shutil.copy(filename, os.path.join(self.faulty_directory_done, os.path.basename(filename).replace(".mp4", "_to_delete.mp4")))
        if os.path.exists(filename):
            os.remove(filename)
        else:
            print("Error: No File")

    def OnBtnTrueAlert(self):
        filename = self.filename
        if len(self.front_videos_list) > 1:
            del (self.front_videos_list[0])
            self.filename = self.front_videos_list[0]
            if os.path.exists(self.filename):
                self.loadFrontVideoFile(self.filename)
                self.start_frontCam(True)
        else:
            self.frontCamThread.captured_video.release()
            self.loadFrontVideoFile("NoMoreFiles.mp4")

        if os.path.exists(filename):
            if "front" in filename.lower():
                shutil.copy(filename, os.path.join(self.front_directory_done, os.path.basename(filename)))
            else:
                shutil.copy(filename, os.path.join(self.back_directory_done, os.path.basename(filename)))
        if os.path.exists(filename):
            os.remove(filename)
        else:
            print("Error: No File")

    def OnBtnFalseAlert(self):
        filename = self.filename
        if len(self.front_videos_list) > 1:
            del (self.front_videos_list[0])
            self.filename = self.front_videos_list[0]
            if os.path.exists(self.filename):
                self.loadFrontVideoFile(self.filename)
                self.start_frontCam(True)
        else:
            self.frontCamThread.captured_video.release()
            self.loadFrontVideoFile("NoMoreFiles.mp4")

        if os.path.exists(filename):

            if "false" in filename.lower():
                shutil.copy(filename, os.path.join(self.faulty_directory_done, os.path.basename(filename)))
            else:
                if "front" in filename.lower():
                    new_name = os.path.basename(filename).replace("Front_Distance_", "").replace("Front_Collision_", "")
                    new_name = "_".join(new_name.split("_")[1:])
                    new_name = "Front_False_" + new_name
                    new_name = new_name.replace("Front_Distance_Bike_False_", "Front_False_Bike_")
                    new_name = new_name.replace("Front_Collision_Bike_False_", "Front_False_Bike_")

                    shutil.copy(filename, os.path.join(self.front_directory_done, new_name))
                else:
                    new_name = os.path.basename(filename).split("Spot")[1]
                    new_name = "_".join(new_name.split("_")[1:])
                    new_name = "Blind_Spots_False_" + new_name
                    shutil.copy(filename, os.path.join(self.back_directory_done, new_name))

            os.remove(filename)

    def GetAlertName(self, filename):
        if "Front" in filename and "blind" not in filename:
            if "Collision" in filename:
                return "Collision"
            if "Distance" in filename:
                return "Safe Distance"
            return "Alert = Collision or Safe Distance"

        if "Left" in filename and "Right" in filename:
            return "Alert = Both Blind Spots"
        if "Left" in filename:
            return "Alert = Left Blind Spot"
        return "Alert Type = Right Blind Spot"

    def OnAppStart(self):
        self.frontCamThread.pause = True
        self.front_videos_list = [self.video_directory + "/" + x for x in os.listdir(self.video_directory)
                                  if x.endswith("mp4")]
        if len(self.front_videos_list) == 0:
            self.loadFrontVideoFile("NoMoreFiles.mp4")

            return
        self.filename = self.front_videos_list[0]
        self.base_dirname = os.path.dirname(os.path.dirname(self.filename))
        self.front_directory_done = os.path.join(self.base_dirname, "Front_Done")
        self.back_directory_done = os.path.join(self.base_dirname, "Back_Done")
        self.faulty_directory_done = os.path.join(self.base_dirname, "Mislabled")

        if not os.path.exists(self.front_directory_done):
            os.mkdir(self.front_directory_done)
        if not os.path.exists(self.back_directory_done):
            os.mkdir(self.back_directory_done)
        if not os.path.exists(self.faulty_directory_done):
            os.mkdir(self.faulty_directory_done)

        self.loadFrontVideoFile(self.filename)
        self.indices = get_file_indices('/media/rider/4689-5BB2/Front_Alerts/',
                                        '/media/rider/6575-F30A2/Blindspot_All/',
                                        os.path.dirname(self.video_directory))

        ind = np.where(np.asarray(self.front_videos_list) == self.filename)[0]
        try:
            self.front_videos_list = self.front_videos_list[ind:]
        except:
            pass

        if len(self.front_videos_list) > 1:
            pos = np.where(np.asarray(self.front_videos_list) == self.filename)[0]
            if len(pos) > 0:
                current_file_position = pos[0]
                self.front_videos_list = self.front_videos_list[current_file_position + 1:]
        else:
            self.loadFrontVideoFile("NoMoreFiles.mp4")
        list_of_folders = [os.path.join(self.video_directory, x) for x in os.listdir(self.video_directory)
                           if os.path.isdir(os.path.join(self.video_directory, x))]
        for folder in list_of_folders:
            list_of_files = [os.path.join(folder, x) for x in os.listdir(folder)]
            [self.front_videos_list.append(file) for file in list_of_files if self.is_front_footage(file)]
        self.label.setText(self.GetAlertName(self.filename))

        new_color = "rgb(255, 0, 0)"
        self.label.setStyleSheet(f"color: {new_color};")

    def OnBtnFrontOpen(self):
        self.frontCamThread.pause = True

        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open video', self.video_directory,
                                                         "Video files (*.MOV *.mp4 *.avi)")[0]
        if self.filename is not None and self.filename != ('', ''):
            self.base_dirname = os.path.dirname(os.path.dirname(self.filename))
            self.front_directory_done = os.path.join(self.base_dirname, "Front_Done")
            self.back_directory_done = os.path.join(self.base_dirname, "Back_Done")
            self.faulty_directory_done = os.path.join(self.base_dirname, "Mislabled")
            self.label.setText(self.GetAlertName(self.filename))

            if not os.path.exists(self.front_directory_done):
                os.mkdir(self.front_directory_done)
            if not os.path.exists(self.back_directory_done):
                os.mkdir(self.back_directory_done)
            if not os.path.exists(self.faulty_directory_done):
                os.mkdir(self.faulty_directory_done)
            if self.filename != ('', ''):
                self.video_directory = os.path.dirname(self.filename)
            self.loadFrontVideoFile(self.filename)
            if self.video_directory == '':
                return
            self.front_videos_list = [self.video_directory + "/" + x for x in os.listdir(self.video_directory)
                                      if ".mp4" in x]
            ind = np.where(np.asarray(self.front_videos_list) == self.filename)[0]
            try:
                self.front_videos_list = self.front_videos_list[ind:]
            except:
                pass

            if len(self.front_videos_list) > 1:
                pos = np.where(np.asarray(self.front_videos_list) == self.filename)[0]
                if len(pos) > 0:
                    current_file_position = pos[0]
                    self.front_videos_list = self.front_videos_list[current_file_position + 1:]
            else:
                self.loadFrontVideoFile("NoMoreFiles.mp4")

            list_of_folders = [os.path.join(self.video_directory, x) for x in os.listdir(self.video_directory)
                               if os.path.isdir(os.path.join(self.video_directory, x))]
            for folder in list_of_folders:
                list_of_files = [os.path.join(folder, x) for x in os.listdir(folder)]
                [self.front_videos_list.append(file) for file in list_of_files if self.is_front_footage(file)]

    # start/stop the front camera thread
    def start_frontCam(self, isStarted):
        if isStarted:
            self.btnStartFront.setIcon(QIcon(":/newPrefix/resources/pause.png"))
            self.frontCamThread.pause = False
        else:
            self.btnStartFront.setIcon(QIcon(":/newPrefix/resources/play.png"))
            self.frontCamThread.pause = True

    # When clicking "Start/Stop" button for front camera
    def OnbtnStartFront(self):
        if self.frontCamURL == "":
            return

        self.isFrontStarted = not self.isFrontStarted
        self.start_frontCam(self.isFrontStarted)

    def seek_front(self, seek_pos):
        self.frontCamThread.pause = True
        self.frontCamThread.frameStartTime = seek_pos
        self.frontCamThread.seekFrame = True
        self.isFrontStarted = False

    # When clicking "Go-to-Start" button for front camera
    def OnRefreshFront(self):
        if self.frontCamURL == "":
            return
        self.frontCamThread.pause = True
        self.isFrontStarted = False

        self.loadFrontVideoFile(self.filename)

        self.btnStartFront.setIcon(QIcon(":/newPrefix/resources/play.png"))
        self.label.setText(self.GetAlertName(self.filename))

        self.sliderFront.setValue(0)
        self.seek_front(0)



    def OnSliderMovedFront(self):
        self.frontCamThread.pause = True

        self.isAllStarted = False

        if self.frontCamURL == "":
            self.sliderFront.setValue(0)
            return

        curVal = self.sliderFront.value()
        self.seek_front(curVal)

    def OnSliderChangedFront(self):
        if self.frontCamURL == "":
            self.sliderFront.setValue(0)
            return
        if self.frontCamThread.pause:
            curVal = self.sliderFront.value()
            self.seek_front(curVal)
            self.btnStartFront.setIcon(QIcon(":/newPrefix/resources/play.png"))

    # When clicking "Open" button for back camera
    # def OnBtnBackOpen(self):
    #     self.frontCamThread.pause = True
    #     self.backCamThread.pause = True
    #
    #     self.btnStartBack.setIcon(QIcon(":/newPrefix/resources/play.png"))
    #
    #     if self.back_directory == './':
    #         self.back_directory = self.video_directory
    #
    #     filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open video', self.back_directory,
    #                                                      "Video files (*.MOV *.mp4 *.avi)")
    #     if filename is not None and filename != ('', ''):
    #         self.back_directory = os.path.dirname(filename[0])
    #
    #         front_filename = self.find_corresponding_front_video_filename(filename[0])
    #         if front_filename is not None:
    #             self.loadFrontVideoFile(front_filename)
    #
    #         self.front_videos_list = [self.back_directory + "/" + x for x in os.listdir(self.back_directory)
    #                                   if x.lower().find("front") != -1 and x.lower().find("blind") != -1
    #                                   and (x.find('mp4') != -1 or x.find('avi') != -1) and x != filename]

    # start/stop the back camera thread
    # When clicking setting menu button
    def OnSetting(self):
        settings = SettingsWindow(self)
        settings.exec_()


    def toggleOFF(self):
        globalStuff.enableOF = not globalStuff.enableOF

        self.frontCamThread.useOF = globalStuff.enableOF

        self.frontCamThread.frameStartTime = max(self.frontCamThread.frameStartTime - 1, 0)
        self.frontCamThread.seekFrame = True

    def eventFilter(self, o, e):
        if e.type() == QtCore.QEvent.MouseMove:
            self.frontHover = False
            self.backHover = False

            if o == self.imgFrontBox:
                self.frontHover = True

            self.mouseP = [e.localPos().x(), e.localPos().y()]
        return super().eventFilter(o, e)


    def drawFrame(self, image, box):
        rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        original_h, original_w, ch = rgbImage.shape

        boxWidth = box.width()
        boxHeight = box.height()

        scaled_width = int(math.floor(boxWidth))
        scaled_height = int(math.floor(boxWidth / original_w * original_h))

        resizedImage = cv2.resize(rgbImage, (scaled_width, scaled_height))
        h, w, ch = resizedImage.shape
        stride = ch * w

        qtImage = QImage(resizedImage.data, w, h, stride, QImage.Format_RGB888)

        yOffset = int((boxHeight - scaled_height) / 2)

        pixmap = QPixmap(boxWidth, boxHeight)
        painter = QPainter()
        painter.begin(pixmap)
        painter.fillRect(0, 0, boxWidth, boxHeight, QColor(0, 0, 0))
        painter.drawImage(QRect(0, yOffset, scaled_width, scaled_height), qtImage)

        font = painter.font()
        font.setPixelSize(20)
        painter.setFont(font)
        outline_pen = QPen(QColor(Qt.black))
        painter.setPen(outline_pen)

        rectangle = self.rect()

        painter.setPen(Qt.white)
        painter.drawText(rectangle, 0, str(self.sliderFront.value()))

        painter.end()

        box.setPixmap(pixmap)
        box.update(QRect(0, 0, boxWidth, boxHeight))

    def tick(self):


        if self.frontImage is not None:
            self.drawFrame(self.frontImage, self.imgFrontBox)
    #
    # def drawBirdViewElements(self, thread, image):
    #     for Entry in thread.vehicleMatrix:
    #         Entry["SmoothedDistances"] = thread.SmoothArray(Entry["Distances"])
    #         Entry["SmoothedAngles"] = thread.SmoothArray(Entry["Angles"])
    #         x = 480 + int((Entry["SmoothedDistances"][-1] + 3) *
    #                       np.sin(Entry["SmoothedAngles"][-1] * np.pi / 360) * 1280 / 40)
    #         y = 600 - int((Entry["SmoothedDistances"][-1] + 3) *
    #                       np.cos(Entry["SmoothedAngles"][-1] * np.pi / 360) * 720 / 40)
    #
    #         color = (255, 255, 255)
    #         if Entry["Alert State"] != 0:
    #             color = (255, 0, 0)
    #         if Entry["SmoothedDistances"][-1] > 100:
    #             continue
    #         #######
    #
    #         if 3 * np.pi/4 > Entry["Rotations"][-1] > np.pi/4:
    #             cv2.rectangle(image, (int(x - 50), y - 30), (int(x + 50), y), color, -1)
    #         else:
    #             cv2.rectangle(image, (int(x - 30), y - 100), (int(x + 30), y), color, -1)
    #
    #         cv2.putText(image, str(Entry["id"]), (int(x - 10), y - 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
    #                     (0, 255, 255), 1, cv2.LINE_AA)
    #         DrawHistory = False
    #         if DrawHistory:
    #             xHistory = 480 + ((Entry["SmoothedDistances"] + 3) *
    #                               np.sin(Entry["SmoothedAngles"] * np.pi / 360) * 1280 / 40)
    #             yHistory = 600 - ((Entry["SmoothedDistances"] + 3) *
    #                               np.cos(Entry["SmoothedAngles"] * np.pi / 360) * 720 / 40)
    #             yHistory = yHistory.astype(np.int16)
    #             xHistory = xHistory.astype(np.int16)
    #
    #             for x, y in zip(xHistory, yHistory):
    #                 cv2.rectangle(image, (int(x - 5), y - 5), (int(x + 5), int(y)), (0, 0, 255), -1)
    #
    #     return image
    #
    # def OnRearBirdsViewButtonPressed(self):
    #     self.BackImageMode = "Bird's View"
    #
    # def OnFrontBirdsViewButtonPressed(self):
    #     self.FrontImageMode = "Bird's View"
    #
    # def OnRearNormalViewButtonPressed(self):
    #     self.FrontImageMode = "Normal"
    #
    # def OnFrontNormalViewButtonPressed(self):
    #     self.BackImageMode = "Normal"

    def exit(self):
        if self.frontCamThread.isRunning():
            self.frontCamThread.pause = True
            self.frontCamThread.terminate()
        # globalStuff.alertThread.exit()

        time.sleep(0.1)

        QtCore.QCoreApplication.instance().quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    app.exec_()

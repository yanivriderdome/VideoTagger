import os.path

import cv2
import numpy as np
import argparse
import shutil
from moviepy.video.io.VideoFileClip import VideoFileClip

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


def find_missing_numbers(nums):
    missing_numbers = []
    for i in range(nums[0], nums[-1] + 1):
        if i not in nums:
            missing_numbers.append(i)
    return missing_numbers


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
    filenames_back = [filename for filename in filenames_back if
                      "False" not in filename and "Spot_Marginal" not in filename]
    indices = {'Left_Blind_Spot': 0, 'Right_Blind_Spot': 0, 'Bike_Left_Blind_Spot': 0, 'Bike_Right_Blind_Spot': 0,
               'Left_And_Right_Blind_Spot': 0, 'Bike_Left_And_Right_Blind_Spot': 0, 'Front_Collision': 0,
               'Front_Collision_Side': 0, 'Front_Collision_Front': 0,
               'Front_Distance': 0, 'Front_Collision_Truck': 0,
               'Front_Distance_Truck': 0, 'Front_Collision_Bike': 0,
               'Front_Distance_Bike': 0, 'Front_Collision_Bus': 0,
               'Front_Distance_Bus': 0, 'Front_Collision_Traffic': 0,
               'Front_Distance_Traffic': 0, 'Front_Collision_Night': 0}

    missing_indices = {'Left_Blind_Spot': [], 'Right_Blind_Spot': [], 'Bike_Left_Blind_Spot': [],
                       'Bike_Right_Blind_Spot': [],
                       'Left_And_Right_Blind_Spot': [], 'Bike_Left_And_Right_Blind_Spot': [], 'Front_Collision': [],
                       'Front_Distance': []}

    for name_type in indices:
        print("getting file index for", name_type)
        if "Blind" in name_type:
            filenames = filenames_back
        else:
            filenames = filenames_front
        filenames = [filename for filename in filenames if filename.startswith(name_type)]
        numbers = [filename[len(name_type) + 1:].lstrip().split("_")[0] for filename in filenames]
        if len(numbers) > 0:
            numbers = sorted([int(number) for number in numbers if number.isdigit()])
            missing_indices[name_type] = find_missing_numbers(numbers)
            if len(numbers) > 0:
                indices[name_type] = 1 + max(numbers)
    return indices, missing_indices


def is_video_file(x):
    if x.find('mp4') != -1 or x.find('avi') != -1 or x.find('MOV') != -1:
        return True
    return False


class Ui(QtWidgets.QMainWindow):
    def __init__(self):

        # Get a list of all available COM ports
        self.LoadAllMovies = True
        self.filename = ''
        self.new_filename = ''
        self.video_directory = 'I:/Videos/New_Alerts/New'
        self.front_videos_list = ['']
        self.frontHover = False
        self.frontImage = None
        self.FrontFrameNum = -1
        self.FrontStuckCounter = 0
        self.BackStuckCounter = 0
        self.front_directory_done = ""
        self.base_dirname = ""
        self.front_directory_done = ""
        self.back_directory_done = ""
        self.faulty_directory_done = ""
        self.to_delete_directory = ""

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
        self.StartFrame = 0
        self.EndFrame = -1

        self.StartFrameBox = self.findChild(QtWidgets.QLineEdit, 'StartFrameBox')
        self.StartFrameBox.textChanged.connect(self.startFrameTextChanged)
        self.EndFrameBox = self.findChild(QtWidgets.QLineEdit, 'EndFrameBox')
        self.EndFrameBox.textChanged.connect(self.endFrameTextChanged)

        self.FilenameBox = self.findChild(QtWidgets.QLineEdit, 'FileNameBox')
        self.FilenameBox.textChanged.connect(self.FilenameChanged)

        self.btnTrueAlert = self.findChild(QtWidgets.QPushButton, 'btnTrueAlert')
        self.btnTrueAlert.clicked.connect(self.OnBtnTrueAlert)
        self.btnTrueAlert = self.findChild(QtWidgets.QPushButton, 'btnCollisionAlert')
        self.btnTrueAlert.clicked.connect(self.OnBtnCollisionAlert)
        self.btnTrueAlert = self.findChild(QtWidgets.QPushButton, 'btnDistanceAlert')
        self.btnTrueAlert.clicked.connect(self.OnBtnDistanceAlert)

        self.btnFalseAlert = self.findChild(QtWidgets.QPushButton, 'btnFalseAlert')
        self.btnFalseAlert.clicked.connect(self.OnBtnFalseAlert)
        self.btnDouble = self.findChild(QtWidgets.QPushButton, 'btnDouble')
        self.btnDouble.clicked.connect(self.OnBtnDelete)

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

        self.cropVideo = self.findChild(QtWidgets.QPushButton, 'btnCrop')
        self.cropVideo.clicked.connect(self.OnButtonCrop)
        self.copyVideo = self.findChild(QtWidgets.QPushButton, 'btnMove')
        self.copyVideo.clicked.connect(self.OnButtonCopy)

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
    # def extract_frames(self, input_video, start_frame, end_frame, output_video):
    #     if os.path.exists(output_video):
    #         output_video = output_video.replace(".mp4","(1).mp4")
    #     cap = cv2.VideoCapture(input_video)
    #     if type(start_frame) == str and len(start_frame) == 0:
    #         start_frame = 0
    #     start_frame = int(start_frame)
    #     if end_frame == '':
    #         end_frame = -1
    #     end_frame = int(end_frame)
    #     fps = cap.get(cv2.CAP_PROP_FPS)
    #     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #
    #     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #     out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    #
    #     cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    #     if end_frame == -1:
    #         end_frame = float('inf')
    #
    #     frame_count = -1
    #     while cap.isOpened() and frame_count <= end_frame:
    #         ret, frame = cap.read()
    #         if frame_count < start_frame:
    #             frame_count += 1
    #             continue
    #         if ret:
    #             out.write(frame)
    #         else:
    #             break
    #         frame_count += 1
    #     cap.release()
    #     out.release()
    #     cv2.destroyAllWindows()
    #     # os.remove(input_video)
    #     self.OnRefreshFront()

    def extract_frames(self,input_filename, start_frame, end_frame, out_filename):
        if os.path.exists(out_filename):
            out_filename = out_filename.replace(".mp4","(1).mp4")
        video = VideoFileClip(input_filename)
        start_time = float(start_frame) / video.fps
        end_time = video.duration

        if end_frame != '':
            end_time = float(end_frame) / video.fps

        self.OnRefreshFront()

        cut_video = video.subclip(start_time, end_time)
        cut_video.write_videofile(out_filename, fps=30)
        cut_video.close()

    def startFrameTextChanged(self, text):
        self.StartFrame = text

    def endFrameTextChanged(self, text):
        self.EndFrame = text

    def FilenameChanged(self, text):
        self.new_filename = text

    def OnButtonCrop(self):
        if "front" in self.filename.lower():
            out_filename = os.path.join(self.front_directory_done, os.path.basename(self.new_filename))
        else:
            out_filename = os.path.join(self.back_directory_done, os.path.basename(self.new_filename))

        self.extract_frames(self.filename, self.StartFrame, self.EndFrame, out_filename)

        return
    def OnButtonCopy(self):
        if "front" in self.filename.lower():
            out_filename = os.path.join(self.front_directory_done, os.path.basename(self.new_filename))
        else:
            out_filename = os.path.join(self.back_directory_done, os.path.basename(self.new_filename))
        shutil.copy(self.filename, out_filename)
        self.OnRefreshFront()

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

    def loadVideoFile(self, filename):
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

    def load_next_video(self):
        if len(self.front_videos_list) > 1:
            del (self.front_videos_list[0])
            self.filename = self.front_videos_list[0]
            self.new_filename = os.path.basename(self.filename)
            self.FilenameBox.setText(self.new_filename)
            self.StartFrameBox.setText("0")
            if os.path.exists(self.filename):
                self.loadVideoFile(self.filename)
                # self.start_frontCam(True)
        else:
            self.frontCamThread.captured_video.release()
            self.loadVideoFile("NoMoreFiles.mp4")
            self.FixFilenames()
            # if os.path.exists(self.video_directory):
            #     for file in os.listdir(self.video_directory):
            #         os.remove(os.path.join(self.video_directory, file))
        self.btnStartFront.setIcon(QIcon(":/newPrefix/resources/play.png"))
        self.frontCamThread.pause = True

    def OnBtnFaulty(self):
        filename = self.new_filename

        self.load_next_video()
        if os.path.exists(filename):
            shutil.copy(filename, os.path.join(self.faulty_directory_done, filename))
            os.remove(filename)
        else:
            print("Error: no file")

    def OnBtnDelete(self):
        filename = self.new_filename
        self.load_next_video()
        full_filename = os.path.join(self.video_directory, filename)
        if os.path.exists(full_filename):
            try:
                os.remove(full_filename)
            except:
                if os.path.exists(full_filename):
                    shutil.copy(full_filename, os.path.join(self.to_delete_directory,
                                                            filename.replace(".mp4", "_to_delete.mp4")))

                print("error: could not delete", full_filename)
        else:
            print("Error: No File")

    def OnBtnTrueAlert(self):
        filename = self.new_filename
        self.load_next_video()
        full_filename = os.path.join(self.video_directory, filename)

        if os.path.exists(full_filename):
            if "front" in filename.lower():
                shutil.copy(full_filename, os.path.join(self.front_directory_done, filename))
            else:
                shutil.copy(full_filename, os.path.join(self.back_directory_done, filename))
        if os.path.exists(full_filename):
            os.remove(full_filename)
        else:
            print("Error: No File")
    def OnBtnCollisionAlert(self):
        filename = self.new_filename.replace("False", "Collision_0000")
        self.load_next_video()
        full_filename = os.path.join(self.video_directory, filename)

        if os.path.exists(full_filename):
            if "front" in filename.lower():
                shutil.copy(full_filename, os.path.join(self.front_directory_done, filename))
            else:
                shutil.copy(full_filename, os.path.join(self.back_directory_done, filename))
        if os.path.exists(full_filename):
            os.remove(full_filename)
        else:
            print("Error: No File")
    def OnBtnDistanceAlert(self):
        filename = self.new_filename.replace("False", "Distance_0000")
        self.load_next_video()
        full_filename = os.path.join(self.video_directory, filename)

        if os.path.exists(full_filename):
            if "front" in filename.lower():
                shutil.copy(full_filename, os.path.join(self.front_directory_done, filename))
            else:
                shutil.copy(full_filename, os.path.join(self.back_directory_done, filename))
        if os.path.exists(full_filename):
            os.remove(full_filename)
        else:
            print("Error: No File")

    def OnBtnFalseAlert(self):
        filename = self.new_filename
        self.load_next_video()
        full_filename = os.path.join(self.video_directory, filename)

        if os.path.exists(full_filename):
            if "false" in filename.lower():
                if "front" in filename.lower() and not "blind" in filename.lower() :
                    shutil.copy(full_filename, os.path.join(self.front_directory_done, filename))
                else:
                    shutil.copy(full_filename, os.path.join(self.back_directory_done, filename))
            else:
                if "front" in filename.lower():
                    new_name = os.path.basename(filename).replace("Front_Distance_", "").replace("Front_Collision_", "")
                    new_name = "_".join(new_name.split("_")[1:])
                    new_name = "Front_False_" + new_name
                    new_name = new_name.replace("Front_Distance_Bike_False_", "Front_False_Bike_")
                    new_name = new_name.replace("Front_Collision_Bike_False_", "Front_False_Bike_")

                    shutil.copy(full_filename, os.path.join(self.front_directory_done, new_name))
                else:
                    new_name = os.path.basename(filename).split("Spot")[1]
                    new_name = "_".join(new_name.split("_")[1:])
                    new_name = "Blind_Spots_False_" + new_name
                    shutil.copy(full_filename, os.path.join(self.back_directory_done, new_name))
            try:
                os.remove(full_filename)
            except:
                pass
        self.OnRefreshFront()

    def set_directories(self):
        self.base_dirname = os.path.dirname(os.path.dirname(self.filename))
        self.front_directory_done = os.path.join(self.base_dirname, "Front_Done")
        self.back_directory_done = os.path.join(self.base_dirname, "Back_Done")
        self.faulty_directory_done = os.path.join(self.base_dirname, "Mislabled")
        self.to_delete_directory = os.path.join(self.base_dirname, "Delete")

        if not os.path.exists(self.front_directory_done):
            os.mkdir(self.front_directory_done)
        if not os.path.exists(self.back_directory_done):
            os.mkdir(self.back_directory_done)
        if not os.path.exists(self.faulty_directory_done):
            os.mkdir(self.faulty_directory_done)
        if not os.path.exists(self.to_delete_directory):
            os.mkdir(self.to_delete_directory)

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

    def get_alert_type(self, filename):
        if filename.startswith('Front_Collision_Side'):
            return 'Front_Collision_Side'
        if filename.startswith('Front_Collision_Front'):
            return 'Front_Collision_Front'

        for alert_type in self.indices.keys():
            if filename.startswith(alert_type):
                return alert_type
        return 'None'

    def FixFilenames(self):
        out_folder = os.path.dirname(self.video_directory)
        self.indices, missing_indices = get_file_indices('/media/rider/4689-5BB2/Front_Alerts/',
                                                              '/media/rider/6575-F30A/Blindspot_All/',
                                                              os.path.dirname(self.video_directory))

        print("Fix Filenames")
        for root, dirs, files in os.walk(out_folder):
            for directory in dirs:
                if not os.path.exists(os.path.join(out_folder, directory)) or "done" not in directory.lower():
                    continue
                for filename in os.listdir(os.path.join(out_folder, directory)):
                    full_filename = os.path.join(os.path.join(out_folder, directory), filename)

                    if "False" in filename:
                        continue
                    alert_type = self.get_alert_type(filename)

                    if alert_type + "Marginal" in filename or alert_type == 'None' or self.indices[alert_type] < 3:
                        continue
                    if len(missing_indices[alert_type]) > 0:
                        file_number = missing_indices[alert_type][0]
                        missing_indices[alert_type] = missing_indices[alert_type][1:]
                    else:
                        file_number = self.indices[alert_type]
                        self.indices[alert_type] += 1
                    new_filename = filename.split(alert_type)[1]
                    new_filename = [x for x in new_filename.split("_") if x != '']
                    new_filename[0] = '{:04d}'.format(file_number)
                    new_filename = alert_type + "_" + "_".join(new_filename)
                    new_filename = os.path.join(os.path.join(out_folder, directory), new_filename)
                    if full_filename != new_filename:
                        print("moving", filename, "to", new_filename)
                        shutil.copy(full_filename, new_filename)
                        os.remove(full_filename)
        print("Finished Fixing Filename")
        return

    def OnAppStart(self):
        self.btnStartFront.setIcon(QIcon(":/newPrefix/resources/pause.png"))

        self.frontCamThread.pause = True
        self.front_videos_list = [self.video_directory + "/" + x for x in os.listdir(self.video_directory)
                                  if x.endswith("mp4")]

        if len(self.front_videos_list) == 0:
            self.loadVideoFile("NoMoreFiles.mp4")
            self.FixFilenames()
            return
        self.filename = self.front_videos_list[0]
        self.new_filename = os.path.basename(self.filename)
        self.FilenameBox.setText(self.new_filename)

        self.set_directories()
        self.loadVideoFile(self.filename)
        #
        # ind = np.where(np.asarray(self.front_videos_list) == self.filename)[0]
        # try:
        #     self.front_videos_list = self.front_videos_list[ind:]
        # except:
        #     try:
        #         self.front_videos_list = self.front_videos_list[ind[0]:]
        #     except:
        #         pass

        if len(self.front_videos_list) > 0:
            pos = np.where(np.asarray(self.front_videos_list) == self.filename)[0]
            if len(pos) > 0:
                current_file_position = pos[0]
                self.front_videos_list = self.front_videos_list[current_file_position + 1:]
        else:
            self.loadVideoFile("NoMoreFiles.mp4")
            self.FixFilenames()

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
        self.new_filename = os.path.basename(self.filename)
        self.FilenameBox.setText(self.new_filename)

        if self.filename is not None and self.filename != ('', ''):
            self.set_directories()
            if self.filename != ('', ''):
                self.video_directory = os.path.dirname(self.filename)
            self.loadVideoFile(self.filename)
            if self.video_directory == '':
                return
            self.front_videos_list = [self.video_directory + "/" + x for x in os.listdir(self.video_directory)
                                      if ".mp4" in x]
            # ind = np.where(np.asarray(self.front_videos_list) == self.filename)[0]
            # try:
            #     self.front_videos_list = self.front_videos_list[ind:]
            # except:
            #     pass

            if len(self.front_videos_list) > 0:
                pos = np.where(np.asarray(self.front_videos_list) == self.filename)[0]
                if len(pos) > 0:
                    current_file_position = pos[0]
                    self.front_videos_list = self.front_videos_list[current_file_position + 1:]
            else:
                self.loadVideoFile("NoMoreFiles.mp4")
                # self.FixFilenames()

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
        self.start_frontCam(self.isFrontStarted)

        self.isFrontStarted = not self.isFrontStarted

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

        self.loadVideoFile(self.filename)
        self.StartFrame = 0
        self.EndFrame = -1
        self.btnStartFront.setIcon(QIcon(":/newPrefix/resources/pause.png"))

        # self.btnStartFront.setIcon(QIcon(":/newPrefix/resources/play.png"))
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
    #             self.loadVideoFile(front_filename)
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

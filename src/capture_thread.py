# from PyQt5.QtGui import *
import numpy as np
from PyQt5.QtCore import *
import cv2
import globalStuff


class Thread(QThread):
    changePixmap = pyqtSignal(np.ndarray, int, int, bool)
    alertTypeSignal = pyqtSignal(int, str)
    finishedSignal = pyqtSignal(bool, int)

    def __init__(self, parent, cam_id, cam_url, start_frame, video_speed):
        QThread.__init__(self, parent)
        self.parent = parent
        self.camID = cam_id
        self.camURL = cam_url
        self.frameStartTime = start_frame
        self.videoSpeed = video_speed
        self.pause = True
        self.finished = True
        self.load_more_movies = True
        self.fail_count = 0
        self.frame_num = 0

        self.seekFrame = False
        self.captured_video = None
        self.analyticSignalThreshold = 0.2

        self.image_height = 720
        self.image_width = 1280


    def StartNewVideo(self, filename):
        if self.captured_video is not None:
            self.captured_video.release()

        self.captured_video = cv2.VideoCapture(filename)
        return int(self.captured_video.get(cv2.CAP_PROP_FRAME_COUNT))


    def run(self):
        counter = 1
        sleep_counter = 0
        self.pause = False
        while True:
            self.finished = False
            QThread.msleep(33)

            if self.pause and not self.seekFrame:
                sleep_counter += 1
                continue

            if self.seekFrame:
                self.frame_num = self.frameStartTime
                self.captured_video.set(cv2.CAP_PROP_POS_FRAMES, self.frameStartTime)

            ret, frame = self.captured_video.read()

            if not ret:
                self.fail_count += 1
                if self.fail_count >= 5:
                    self.pause = True
                self.seekFrame = False
                self.finished = True
                if self.load_more_movies:
                    return

                continue

            self.frameStartTime += 1
            self.frame_num += 1

            if counter % self.videoSpeed:
                counter += 1
                continue
            counter = 1

            self.changePixmap.emit(frame, self.camID, self.frame_num, not self.seekFrame)

            self.seekFrame = False

        self.finishedSignal.emit(True, self.camID)

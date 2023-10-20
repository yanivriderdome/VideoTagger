import cv2
import numpy as np
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from perspectiveDistance import PerspectiveDistance, CalibrationSettings


class CalibrationWindow(QtWidgets.QMainWindow):
    def __init__(self, parent, cameraDirection, frame):
        super(CalibrationWindow, self).__init__(parent)
        uic.loadUi('form.ui', self)

        self.mouseP = [0, 0]
        self.mouseWentDown = False
        self.mouseWentUp = False
        self.mouseDown = False

        self.hoveredPoint = -1

        print(self.parent)

        calibration = None

        if cameraDirection == "front":
            calibration = CalibrationSettings("./config/calibration_front.txt")
        elif cameraDirection == "back":
            calibration = CalibrationSettings("./config/calibration_back.txt")

        self.calibration = calibration
        self.cameraDirection = cameraDirection

        self.calibration.imageSize = frame.shape
        self.perspectiveDistance = PerspectiveDistance(self.calibration)

        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.editSizeX = self.findChild(QtWidgets.QLineEdit, 'editSizeX')
        self.editSizeY = self.findChild(QtWidgets.QLineEdit, 'editSizeY')
        self.editRotation = self.findChild(QtWidgets.QLineEdit, 'editRotation')
        self.save = self.findChild(QtWidgets.QPushButton, 'save')

        self.imageFrame = self.findChild(QtWidgets.QLabel, 'imageFrame')
        self.imageFrame.setMouseTracking(True)
        self.imageFrame.installEventFilter(self)

        self.editSizeX.setText(str(self.calibration.xDistance))
        self.editSizeY.setText(str(self.calibration.yDistance))
        self.editRotation.setText(str(self.calibration.rotationAngle))

        self.save.clicked.connect(self.calibration.saveToFile)
        self.editSizeX.textChanged.connect(self.editSizeXCallback)
        self.editSizeY.textChanged.connect(self.editSizeYCallback)
        self.editRotation.textChanged.connect(self.editRotationCallback)

        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.tick)
        self.timer.start()

        # self.imgFrontBox.update(QRect(0, 0, self.imgFrontBoxWidth, self.imgFrontBoxHeight))

        self.show()

    def editSizeXCallback(self, text):
        try:
            self.calibration.xDistance = int(text)
        except (ValueError, TypeError):
            return
        print(f"x set to {self.calibration.xDistance}")

    def editSizeYCallback(self, text):
        try:
            self.calibration.yDistance = int(text)
        except (ValueError, TypeError):
            return
        print(f"y set to {self.calibration.yDistance}")

    def editRotationCallback(self, text):
        try:
            self.calibration.rotationAngle = int(text)
        except (ValueError, TypeError):
            return
        print(f"rot set to {self.calibration.rotationAngle}")

    def tick(self):
        image = self.frame
        height, width, channels = image.shape

        scaledWidth = self.imageFrame.width()
        scaledHeight = (height / width) * scaledWidth

        resized = cv2.resize(image, (int(scaledWidth), int(scaledHeight)), interpolation=cv2.INTER_AREA)

        angle = self.calibration.rotationAngle
        if angle != 0:
            rotationMatrix = cv2.getRotationMatrix2D((resized.shape[1] * 0.5, resized.shape[0]), -angle, 1)
            # get the rotation matrix and rotating point is set to be bottom center of image,
            # and negative angle of the angle
            resized = cv2.warpAffine(resized, rotationMatrix, (
                resized.shape[1], resized.shape[0]))  # rotate the image with the obtained rotation matrix

        if self.mouseWentUp and self.hoveredPoint > -1:
            self.hoveredPoint = -1

        if self.mouseDown and self.hoveredPoint > -1:
            self.calibration.imgPoint[self.hoveredPoint][0] = self.mouseP[0] / scaledWidth
            self.calibration.imgPoint[self.hoveredPoint][1] = self.mouseP[1] / scaledHeight
            self.perspectiveDistance.applySettings(self.calibration)

        pd = self.perspectiveDistance

        # draw the perspective polygon
        for i in range(0, 3):
            resized = cv2.line(resized, (int(pd.imgPoint[i, 0] * scaledWidth), int(pd.imgPoint[i, 1] * scaledHeight)),
                               (int(pd.imgPoint[i + 1, 0] * scaledWidth), int(pd.imgPoint[i + 1, 1] * scaledHeight)),
                               (0, 255, 0), 2)

        resized = cv2.line(resized, (int(pd.imgPoint[3, 0] * scaledWidth), int(pd.imgPoint[3, 1] * scaledHeight)),
                           (int(pd.imgPoint[0, 0] * scaledWidth), int(pd.imgPoint[0, 1] * scaledHeight)), (0, 255, 0),
                           2)

        # show the origin, x and y axes of the perspective drawing
        resized = cv2.putText(resized, "0",
                              (int(pd.imgPoint[0, 0] * scaledWidth), int(pd.imgPoint[0, 1] * scaledHeight)),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        resized = cv2.putText(resized, "x", (int((pd.imgPoint[1, 0] + pd.imgPoint[0, 0]) / 2 * scaledWidth),
                                             int((pd.imgPoint[1, 1] + pd.imgPoint[0, 1]) / 2 * scaledHeight)),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        resized = cv2.putText(resized, "y", (int((pd.imgPoint[3, 0] + pd.imgPoint[0, 0]) / 2 * scaledWidth),
                                             int((pd.imgPoint[3, 1] + pd.imgPoint[0, 1]) / 2 * scaledHeight)),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        resized = pd.drawNonRotatedPerspectiveROI(resized)
        resized = cv2.circle(resized, (int(0.5 * resized.shape[1]), int(1 * resized.shape[0])), 5, (0, 0, 255),
                             -1)  # draw a circle on bottom center point

        hoveredDistance = 99999.0
        self.hoveredPoint = -1

        for i in range(0, 4):
            point = np.array([pd.imgPoint[i, 0] * scaledWidth, pd.imgPoint[i, 1] * scaledHeight])
            resized = cv2.circle(resized, (int(point[0]), int(point[1])), 3, (38, 125, 188), -1)
            distance = cv2.norm(self.mouseP - point)

            if distance < min(hoveredDistance, 20):
                hoveredDistance = distance
                self.hoveredPoint = i

        if self.hoveredPoint > -1:
            # print(f"distance: {hoveredDistance}")
            point = [pd.imgPoint[self.hoveredPoint, 0] * scaledWidth, pd.imgPoint[self.hoveredPoint, 1] * scaledHeight]
            resized = cv2.circle(resized, (int(point[0]), int(point[1])), 4, (62, 215, 250), -1)

        qtImage = QImage(resized.data, scaledWidth, scaledHeight, channels * scaledWidth, QImage.Format_RGB888)
        self.imageFrame.setPixmap(QPixmap.fromImage(qtImage))

        self.mouseWentDown = False
        self.mouseWentUp = False

    def eventFilter(self, o, e):
        if e.type() == QtCore.QEvent.MouseMove:
            self.mouseP = [e.localPos().x(), e.localPos().y()]
            # print(f"mouse x:{self.mouseP[0]} y: {self.mouseP[1]}")
        return super().eventFilter(o, e)

    def mousePressEvent(self, event):
        self.mouseDown = True
        self.mouseWentDown = True
        # print("MOUSE PRESS")

    def mouseReleaseEvent(self, event):
        self.mouseDown = False
        self.mouseWentUp = True
        # print("MOUSE RELEASE")

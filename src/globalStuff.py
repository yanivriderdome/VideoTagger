import cv2

alertThread = None
enableGrid = False
enableOF = False
enableCarWidthDistance = False


class FakeRau:
    def __init__(self):
        self.leftLeds = [(0, 0, 0)] * 8
        self.rightLeds = [(0, 0, 0)] * 8
        self.image = 0

        self.images = {
            "ok": cv2.imread("ui\\resources\\okay.png", cv2.IMREAD_UNCHANGED),
            "stop": cv2.imread("ui\\resources\\stop.png", cv2.IMREAD_UNCHANGED),
            "car": cv2.imread("ui\\resources\\car-front.png", cv2.IMREAD_UNCHANGED),
            "bus": cv2.imread("ui\\resources\\bus-front.png", cv2.IMREAD_UNCHANGED),
            "motorcycle": cv2.imread("ui\\resources\\motorcycle-side.png", cv2.IMREAD_UNCHANGED),
        }
        if self.images['car'] is not None:
            print(self.images['car'].shape)
        #
        # for i in range(0, 8):
        #     self.leftLeds.append((0, 0, 0))
        #
        # for i in range(0, 8):
        #     self.rightLeds.append((0, 0, 0))


fakeRau = FakeRau()

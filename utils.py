from PyQt5.QtGui import *

def alert(window, alert_type, vehicle_type = ""):
    if alert_type == 2:
        fwd_collision_alert(window)
    # elif alert_type == 1:
    #     fwd_safe_dist_alert(self, vehicle_type, 0)
    # elif alert_type == 2:
    #     bwd_blindspot_right_alert(self, vehicle_type)
    # elif alert_type == 3:
    #     bwd_blindspot_left_alert(self, vehicle_type)
    # elif alert_type == 4:
    #     bwd_safe_dist_alert(self, vehicle_type, 0)
    # elif alert_type == 5:
    #     fwd_safe_dist_alert(self, vehicle_type, 1)
    # elif alert_type == 6:
    #     fwd_safe_dist_alert(self, vehicle_type, 2)
    # elif alert_type == 7:
    #     fwd_safe_dist_alert(self, vehicle_type, 3)
    # elif alert_type == 8:
    #     bwd_safe_dist_alert(self, vehicle_type, 1)
    # elif alert_type == 9:
    #     bwd_safe_dist_alert(self, vehicle_type, 2)
    # elif alert_type == 10:
    #     bwd_safe_dist_alert(self, vehicle_type, 3)

def alert_off(parent):
    parent.imgLeftAlert.setPixmap(QPixmap(""))
    parent.ledLeft1.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft2.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft3.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft4.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft5.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft6.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft7.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft8.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")

    parent.imgRightAlert.setPixmap(QPixmap(""))
    parent.ledRight1.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight2.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight3.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight4.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight5.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight6.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight7.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight8.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")

def fwd_collision_alert(parent):
    parent.imgLeftAlert.setPixmap(QPixmap(":/newPrefix/resources/stop.png"))
    parent.ledLeft1.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft2.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft3.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft4.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft5.setStyleSheet(
        "background-image: url(:/newPrefix/resources/red_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft6.setStyleSheet(
        "background-image: url(:/newPrefix/resources/red_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft7.setStyleSheet(
        "background-image: url(:/newPrefix/resources/red_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft8.setStyleSheet(
        "background-image: url(:/newPrefix/resources/red_circle.png);\n"
        "color: rgb(255, 255, 255);")

    parent.imgRightAlert.setPixmap(QPixmap(":/newPrefix/resources/stop.png"))
    parent.ledRight1.setStyleSheet(
        "background-image: url(:/newPrefix/resources/red_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight2.setStyleSheet(
        "background-image: url(:/newPrefix/resources/red_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight3.setStyleSheet(
        "background-image: url(:/newPrefix/resources/red_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight4.setStyleSheet(
        "background-image: url(:/newPrefix/resources/red_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight5.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight6.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight7.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight8.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")

def fwd_safe_dist_alert(parent, vehicle_type, safe_dist_type):
    if vehicle_type == "Car":
        img_src = ":/newPrefix/resources/car-front.png"
    elif vehicle_type == "Bus":
        img_src = ":/newPrefix/resources/bus-front.png"
    elif vehicle_type == "Truck":
        img_src = ":/newPrefix/resources/bus-front.png"
    elif vehicle_type == "Motorcycle":
        img_src = ":/newPrefix/resources/motorcycle-side.png"
    parent.imgLeftAlert.setPixmap(QPixmap(img_src))
    parent.ledLeft1.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft2.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft3.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft4.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    if safe_dist_type == 0:
        parent.ledLeft5.setStyleSheet(
            "background-image: url(:/newPrefix/resources/red_circle.png);\n"
            "color: rgb(255, 255, 255);")
    else:
        parent.ledLeft5.setStyleSheet(
            "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
            "color: rgb(255, 255, 255);")
    if safe_dist_type == 0 or safe_dist_type == 3:
        parent.ledLeft6.setStyleSheet(
            "background-image: url(:/newPrefix/resources/red_circle.png);\n"
            "color: rgb(255, 255, 255);")
    else:
        parent.ledLeft6.setStyleSheet(
            "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
            "color: rgb(255, 255, 255);")
    if safe_dist_type == 1:
        parent.ledLeft7.setStyleSheet(
            "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
            "color: rgb(255, 255, 255);")
    else:
        parent.ledLeft7.setStyleSheet(
            "background-image: url(:/newPrefix/resources/red_circle.png);\n"
            "color: rgb(255, 255, 255);")
    parent.ledLeft8.setStyleSheet(
        "background-image: url(:/newPrefix/resources/red_circle.png);\n"
        "color: rgb(255, 255, 255);")

    parent.imgRightAlert.setPixmap(QPixmap(img_src))
    if safe_dist_type == 0:
        parent.ledRight1.setStyleSheet(
            "background-image: url(:/newPrefix/resources/red_circle.png);\n"
            "color: rgb(255, 255, 255);")
    else:
        parent.ledRight1.setStyleSheet(
            "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
            "color: rgb(255, 255, 255);")
    if safe_dist_type == 0 or safe_dist_type == 3:
        parent.ledRight2.setStyleSheet(
            "background-image: url(:/newPrefix/resources/red_circle.png);\n"
            "color: rgb(255, 255, 255);")
    else:
        parent.ledRight2.setStyleSheet(
            "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
            "color: rgb(255, 255, 255);")
    if safe_dist_type == 1:
        parent.ledRight3.setStyleSheet(
            "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
            "color: rgb(255, 255, 255);")
    else:
        parent.ledRight3.setStyleSheet(
            "background-image: url(:/newPrefix/resources/red_circle.png);\n"
            "color: rgb(255, 255, 255);")
    parent.ledRight4.setStyleSheet(
        "background-image: url(:/newPrefix/resources/red_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight5.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight6.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight7.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight8.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")

def bwd_blindspot_right_alert(parent, vehicle_type):
    if vehicle_type == "Car":
        img_src = ":/newPrefix/resources/car-front.png"
    elif vehicle_type == "Bus":
        img_src = ":/newPrefix/resources/bus-front.png"
    elif vehicle_type == "Truck":
        img_src = ":/newPrefix/resources/bus-front.png"
    elif vehicle_type == "Motorcycle":
        img_src = ":/newPrefix/resources/motorcycle-side.png"

    parent.imgLeftAlert.setPixmap(QPixmap(img_src))
    parent.ledLeft1.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft2.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft3.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft4.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft5.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft6.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft7.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft8.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")

    parent.imgRightAlert.setPixmap(QPixmap(img_src))
    parent.ledRight1.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight2.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight3.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight4.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight5.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight6.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight7.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight8.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")

def bwd_blindspot_left_alert(parent, vehicle_type):
    if vehicle_type == "Car":
        img_src = ":/newPrefix/resources/car-front.png"
    elif vehicle_type == "Bus":
        img_src = ":/newPrefix/resources/bus-front.png"
    elif vehicle_type == "Truck":
        img_src = ":/newPrefix/resources/bus-front.png"
    elif vehicle_type == "Motorcycle":
        img_src = ":/newPrefix/resources/motorcycle-side.png"

    parent.imgLeftAlert.setPixmap(QPixmap(img_src))
    parent.ledLeft1.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft2.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft3.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft4.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft5.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft6.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft7.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft8.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")

    parent.imgRightAlert.setPixmap(QPixmap(img_src))
    parent.ledRight1.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight2.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight3.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight4.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight5.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight6.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight7.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight8.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")

def bwd_safe_dist_alert(parent, vehicle_type, safe_dist_type):
    if vehicle_type == "Car":
        img_src = ":/newPrefix/resources/car-front.png"
    elif vehicle_type == "Bus":
        img_src = ":/newPrefix/resources/bus-front.png"
    elif vehicle_type == "Truck":
        img_src = ":/newPrefix/resources/bus-front.png"
    elif vehicle_type == "Motorcycle":
        img_src = ":/newPrefix/resources/motorcycle-side.png"

    parent.imgLeftAlert.setPixmap(QPixmap(img_src))
    if safe_dist_type == 0:
        parent.ledLeft1.setStyleSheet(
            "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
            "color: rgb(255, 255, 255);")
    else:
        parent.ledLeft1.setStyleSheet(
            "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
            "color: rgb(255, 255, 255);")
    if safe_dist_type == 0 or safe_dist_type == 3:
        parent.ledLeft2.setStyleSheet(
            "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
            "color: rgb(255, 255, 255);")
    else:
        parent.ledLeft2.setStyleSheet(
            "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
            "color: rgb(255, 255, 255);")
    if safe_dist_type == 1:
        parent.ledLeft3.setStyleSheet(
            "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
            "color: rgb(255, 255, 255);")
    else:
        parent.ledLeft3.setStyleSheet(
            "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
            "color: rgb(255, 255, 255);")
    parent.ledLeft4.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft5.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft6.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft7.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledLeft8.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")

    parent.imgRightAlert.setPixmap(QPixmap(img_src))
    parent.ledRight1.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight2.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight3.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    parent.ledRight4.setStyleSheet(
        "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
        "color: rgb(255, 255, 255);")
    if safe_dist_type == 0:
        parent.ledRight5.setStyleSheet(
            "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
            "color: rgb(255, 255, 255);")
    else:
        parent.ledRight5.setStyleSheet(
            "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
            "color: rgb(255, 255, 255);")
    if safe_dist_type == 0 or safe_dist_type == 3:
        parent.ledRight6.setStyleSheet(
            "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
            "color: rgb(255, 255, 255);")
    else:
        parent.ledRight6.setStyleSheet(
            "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
            "color: rgb(255, 255, 255);")
    if safe_dist_type == 1:
        parent.ledRight7.setStyleSheet(
            "background-image: url(:/newPrefix/resources/gray_circle.png);\n"
            "color: rgb(255, 255, 255);")
    else:
        parent.ledRight7.setStyleSheet(
            "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
            "color: rgb(255, 255, 255);")
    parent.ledRight8.setStyleSheet(
        "background-image: url(:/newPrefix/resources/orange_circle.png);\n"
        "color: rgb(255, 255, 255);")





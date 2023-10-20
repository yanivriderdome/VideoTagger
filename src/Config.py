from PyQt5.QtCore import QSettings
from dataclasses import dataclass


@dataclass
class theil_san_result:
    MedianSlope: float
    MedianIntercept: float
    ConfidenceLowerBound: float
    ConfidenceUpperBound: float


settings = [
    {
        'title': 'dimensions (all in centimeters)',
        'fields': [
            {'name': 'car width', 'id': 'car_width', 'value': 180, 'type': int},
            {'name': 'car length', 'id': 'car_length', 'value': 450, 'type': int},
            {'name': 'bus width', 'id': 'bus_length', 'value': 250, 'type': int},
            {'name': 'motorcycle width', 'id': 'motorcycle_width', 'value': 80, 'type': int},
            {'name': 'pedestrian width', 'id': 'pedestrian_width', 'value': 70, 'type': int},
        ]
    },
    {
        'title': 'common alert settings',
        'fields': [
            {'name': 'frame count', 'id': 'alert_frame_count', 'value': 8, 'type': int},
            {'name': 'alert duration, s', 'id': 'alert_duration', 'value': 1.0, 'type': float},
            {'name': 'alert suppression, s', 'id': 'alert_suppression', 'value': 1.0, 'type': float},
        ]
    },
    {
        'title': 'front collision alert',
        'fields': [
            {'name': 'min distance, m', 'id': 'front_collision_distance_min', 'value': 2.0, 'type': float},
            {'name': 'max distance, m', 'id': 'front_collision_distance_max', 'value': 15.0, 'type': float},
            {'name': 'angle', 'id': 'front_collision_angle', 'value': 15.0, 'type': float},

            # (rel speed - how fast the car is getting closer / further away from the motorcycle)
            {'name': 'speed delta (upper limit)', 'id': 'front_collision_rel_speed_high', 'value': -0.15,
             'type': float},
            {'name': 'speed delta (lower limit)', 'id': 'front_collision_rel_speed_low', 'value': 1.0, 'type': float},
        ]
    },
    {
        'title': 'front safe distance',
        'fields': [
            {'name': 'min distance, m', 'id': 'safe_distance_min', 'value': 2.0, 'type': float},
            {'name': 'max distance, m', 'id': 'safe_distance_max', 'value': 10.0, 'type': float},
            {'name': 'angle', 'id': 'safe_distance_angle', 'value': 15.0, 'type': float},

            {'name': 'speed delta (lower limit)', 'id': 'safe_distance_rel_speed_low', 'value': -0.02, 'type': float},
        ]
    },
    {
        'title': 'back collision alert',
        'fields': [
            {'name': 'min distance, m', 'id': 'back_collision_distance_min', 'value': 3.0, 'type': float},
            {'name': 'max distance, m', 'id': 'back_collision_distance_max', 'value': 30.0, 'type': float},
            {'name': 'angle', 'id': 'back_collision_angle', 'value': 15.0, 'type': float},

            # (rel speed - how fast the car is getting closer / further away from the motorcycle)
            {'name': 'speed delta (upper limit)', 'id': 'back_collision_rel_speed_high', 'value': -0.15, 'type': float},
        ]
    },
    {
        'title': 'blindspot alert',
        'fields': [
            {'name': 'min distance, m', 'id': 'blindspot_distance_min', 'value': 2.0, 'type': float},
            {'name': 'max distance, m', 'id': 'blindspot_distance_max', 'value': 10.0, 'type': float},
            {'name': 'angle', 'id': 'blindspot_angle', 'value': 60.0, 'type': float},
            {'name': 'min side angle', 'id': 'blindspot_side_angle_min', 'value': 35.0, 'type': float},
            {'name': 'max side angle', 'id': 'blindspot_side_angle_max', 'value': 60.0, 'type': float},
        ]
    },
]


def find(id: object) -> float:
    for section in settings:
        for field in section['fields']:
            if field['id'] == id:
                # print(f"[config] used {field['id']} : {field['value']}")
                return field['value']

    print(f"[config] setting '{id}' not found")
    return 0


def init():
    loadedSettings = QSettings('config/config.ini', QSettings.IniFormat)

    for i, section in enumerate(settings):
        for j, field in enumerate(section['fields']):
            if loadedSettings.contains(field['id']):
                settings[i]['fields'][j]['value'] = loadedSettings.value(field['id'], type=field['type'])
                print(f"loaded setting {field['name']}: {field['value']}")

from typing import Protocol

import cv2 as cv
from cv2.typing import MatLike
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

from src.constants import INDEX_FINGER_TIP_LANDMARKER_INDEX, MIDDLE_FINGER_TIP_LANDMARKER_INDEX, RING_FINGER_TIP_LANDMARKER_INDEX
from src.vector import Vector


class DrawLandmarksOptions(Protocol):
    def __init__(self,
                 frame: MatLike,
                 hand_landmarks: list[NormalizedLandmark],
                 frame_size: Vector,
                 joint_color: tuple[int, int, int] | tuple[int, int, int, int] = (255, 0, 0),
                 joint_radius: int = 2,
                 index_finger_color: tuple[int, int, int] | tuple[int, int, int, int] = (0, 0, 255),
                 index_finger_radius: int = 2,
                 middle_finger_color: tuple[int, int, int] | tuple[int, int, int, int] = (0, 0, 255),
                 middle_finger_radius: int = 2,
                 ring_finger_color: tuple[int, int, int] | tuple[int, int, int, int] = (0, 0, 255),
                 ring_finger_radius: int = 2):
        self.frame = frame
        self.hand_landmarks = hand_landmarks
        self.frame_size = frame_size
        self.joint_color = joint_color
        self.joint_radius = joint_radius
        self.index_finger_color = index_finger_color
        self.index_finger_radius = index_finger_radius
        self.middle_finger_color = middle_finger_color
        self.middle_finger_radius = middle_finger_radius
        self.ring_finger_color = ring_finger_color
        self.ring_finger_radius = ring_finger_radius


def draw_landmarks(options: DrawLandmarksOptions) -> MatLike:
    frame = options.frame
    hand_landmarks = options.hand_landmarks
    frame_size = options.frame_size
    joint_color = options.joint_color
    joint_radius = options.joint_radius
    index_finger_color = options.index_finger_color
    index_finger_radius = options.index_finger_radius
    middle_finger_color = options.middle_finger_color
    middle_finger_radius = options.middle_finger_radius
    ring_finger_color = options.ring_finger_color
    ring_finger_radius = options.ring_finger_radius

    for index in range(len(hand_landmarks)):
        hand_landmark = hand_landmarks[index]

        point = (
            int(hand_landmark.x * frame_size.x),
            int(hand_landmark.y * frame_size.y)
        )

        if index == INDEX_FINGER_TIP_LANDMARKER_INDEX:
            cv.circle(frame, point, index_finger_radius, index_finger_color, index_finger_radius)
        elif index == MIDDLE_FINGER_TIP_LANDMARKER_INDEX:
            cv.circle(frame, point, middle_finger_radius, middle_finger_color, middle_finger_radius)
        elif index == RING_FINGER_TIP_LANDMARKER_INDEX:
            cv.circle(frame, point, ring_finger_radius, ring_finger_color, ring_finger_radius)
        else:
            cv.circle(frame, point, joint_radius, joint_color, joint_radius)

    return frame

from typing import Protocol

import cv2 as cv
from cv2.typing import MatLike
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

from src.vector import Vector


class DrawRectangleOptions(Protocol):
    def __init__(self,
                 frame: MatLike,
                 hand_landmarks: list[NormalizedLandmark],
                 frame_size: Vector,
                 border_color: tuple[int, int, int] | tuple[int, int, int, int] = (0, 0, 255),
                 border_width: int = 2):
        self.frame = frame
        self.hand_landmarks = hand_landmarks
        self.frame_size = frame_size
        self.border_color = border_color
        self.border_width = border_width


def draw_rectangle(options: DrawRectangleOptions) -> MatLike:
    frame = options.frame
    hand_landmarks = options.hand_landmarks
    frame_size = options.frame_size
    border_color = options.border_color
    border_width = options.border_width

    x_landmarks_points = [item.x for item in hand_landmarks]
    y_landmarks_points = [item.y for item in hand_landmarks]
    min_point = (
        int(min(x_landmarks_points) * frame_size.x),
        int(min(y_landmarks_points) * frame_size.y)
    )
    max_point = (
        int(max(x_landmarks_points) * frame_size.x),
        int(max(y_landmarks_points) * frame_size.y)
    )

    cv.rectangle(frame, min_point, max_point, border_color, border_width)

    return frame

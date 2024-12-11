import cv2 as cv
from cv2.typing import MatLike


class DrawCountdownOptions:
    def __init__(
            self,
            frame: MatLike,
            center_point: tuple[int, int],
            current_time: int | None = 0,
            total_time: int = 0,
            size: tuple[int, int] = (20, 20),
            border_color: tuple[int, int, int] | tuple[int, int, int, int] = (0, 180, 0),
            border_width: int = 5):
        self.frame = frame
        self.center_point = center_point
        self.current_time = current_time
        self.total_time = total_time
        self.size = size
        self.border_color = border_color
        self.border_width = border_width


def draw_countdown(options: DrawCountdownOptions):
    frame = options.frame
    center_point = options.center_point
    current_time = options.current_time
    total_time = options.total_time
    size = options.size
    border_color = options.border_color
    border_width = options.border_width

    angle = -90
    start_angle = (current_time * 360 / total_time) if current_time != None else 360
    end_angle = 360

    cv.ellipse(
        frame,
        center_point,
        size,
        angle,
        start_angle,
        end_angle,
        border_color,
        border_width)

import math

from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

from src.constants import INDEX_FINGER_TIP_LANDMARKER_INDEX, MIDDLE_FINGER_TIP_LANDMARKER_INDEX, RING_FINGER_TIP_LANDMARKER_INDEX
from src.vector import Vector


class Point:
    def __init__(self, point: Vector, frame_size: Vector):
        self.point = point
        self.frame_size = frame_size
        self.position_in_frame = Vector(
            int(self.point.x * self.frame_size.x),
            int(self.point.y * self.frame_size.y)
        )

    @staticmethod
    def from_hand_landmarks(hand_landmarks: list[NormalizedLandmark], finger_index: int, frame_size: Vector) -> 'Point':
        if len(hand_landmarks) > finger_index:
            landmark = hand_landmarks[finger_index]
            finger_point = Vector(landmark.x, landmark.y)
            return Point(finger_point, frame_size)
        raise Exception(f"Landmark index {finger_index} does not exists")

    @staticmethod
    def distance_between_points(a: 'Point', b: 'Point') -> float:
        dx = (a.x - b.x) ** 2
        dy = (a.y - b.y) ** 2
        return math.sqrt(dx + dy)


class Fingers:
    def __init__(self, index: Point, middle: Point, ring: Point):
        self.index = index
        self.middle = middle
        self.ring = ring

    @staticmethod
    def from_hand_landmarks(hand_landmarks: list[NormalizedLandmark], frame_size: Vector) -> 'Fingers':
        return Fingers(
            Point.from_hand_landmarks(hand_landmarks, INDEX_FINGER_TIP_LANDMARKER_INDEX, frame_size),
            Point.from_hand_landmarks(hand_landmarks, MIDDLE_FINGER_TIP_LANDMARKER_INDEX, frame_size),
            Point.from_hand_landmarks(hand_landmarks, RING_FINGER_TIP_LANDMARKER_INDEX, frame_size)
        )

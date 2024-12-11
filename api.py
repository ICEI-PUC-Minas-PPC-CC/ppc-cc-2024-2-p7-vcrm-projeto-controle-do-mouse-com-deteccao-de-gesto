import cv2 as cv
from flask import Flask, request, Response
import jsonpickle
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode
import numpy as np

from src.configs import Configs
from src.constants import MODEL_PATH
from src.draw.countdown import DrawCountdownOptions, draw_countdown
from src.draw.landmarks import DrawLandmarksOptions, draw_landmarks
from src.fingers import Point, Fingers
from src.vector import Vector


app = Flask(__name__)


base_options = BaseOptions(model_asset_path=MODEL_PATH)
hand_landmarker_options = HandLandmarkerOptions(
    base_options=base_options,
    running_mode=RunningMode.IMAGE)
hand_landmarker = HandLandmarker.create_from_options(hand_landmarker_options)


@app.post('/')
def recognize_hand_landmarkers():
    request_data = jsonpickle.decode(request.data)

    captured_image = request_data['captured_image']
    configs = Configs.from_dict(request_data['configs'])
    previous_finger_position = request_data['previous_finger_position']
    mouse_click_left = request_data['mouse_click']['left']
    mouse_click_right = request_data['mouse_click']['right']


    image_array = np.frombuffer(captured_image, np.uint8)
    frame = cv.imdecode(image_array, cv.IMREAD_COLOR)


    frame_height, frame_width, _ = frame.shape
    frame_size = Vector(frame_width, frame_height)
    previous_finger_position = Vector(previous_finger_position['x'], previous_finger_position['y'])


    response_body = {
        'processed_image': None,
        'previous_finger_position': {
            'x': 0,
            'y': 0,
        },
        'mouse_move': {
            'dx': 0,
            'dy': 0,
        },
        'mouse_click': {
            'left': {
                'remaining_time': 0,
                'total_time': 0,
                'should_start': False,
                'should_cancel': False,
            },
            'right': {
                'remaining_time': 0,
                'total_time': 0,
                'should_start': False,
                'should_cancel': False,
            },
        },
    }


    frame = cv.flip(frame, 1)
    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    blurred_frame = cv.GaussianBlur(rgb_frame, (5, 5), 0)
    pre_processed_image = Image(image_format=ImageFormat.SRGB, data=blurred_frame)
    frame = cv.cvtColor(pre_processed_image.numpy_view(), cv.COLOR_RGB2BGR)

    detection_result = hand_landmarker.detect(pre_processed_image)
    hand_landmarks_list: list[list[NormalizedLandmark]] = detection_result.hand_landmarks


    for hand_landmarks_item in hand_landmarks_list:
        fingers = Fingers.from_hand_landmarks(hand_landmarks_item, frame_size)


        # Draw landmarks for each hand_landmark
        if configs.show_landmarkers:
            draw_landmarks(DrawLandmarksOptions(
                frame=frame,
                hand_landmarks=hand_landmarks_item,
                frame_size=frame_size,
            ))


        distance_index_to_middle = Point.distance_between_points(fingers.index.position_in_frame, fingers.middle.position_in_frame)
        distance_middle_to_ring = Point.distance_between_points(fingers.middle.position_in_frame, fingers.ring.position_in_frame)
        # print(f'{distance_index_to_middle:.2f}, {distance_middle_to_ring:.2f}')


        # Move mouse
        if distance_index_to_middle > configs.left_click_max_distance and distance_middle_to_ring > configs.right_click_max_distance:
            if previous_finger_position.x == 0 and previous_finger_position.y == 0:
                previous_finger_position = fingers.index.position_in_frame

            dx = fingers.index.position_in_frame.x - previous_finger_position.x
            dy = fingers.index.position_in_frame.y - previous_finger_position.y

            response_body['mouse_move']['dx'] = dx
            response_body['mouse_move']['dy'] = dy
            response_body['mouse_click']['left']['remaining_time'] = 0
            response_body['mouse_click']['left']['total_time'] = 0
            response_body['mouse_click']['left']['should_start'] = False
            response_body['mouse_click']['left']['should_cancel'] = True
            response_body['mouse_click']['right']['remaining_time'] = 0
            response_body['mouse_click']['right']['total_time'] = 0
            response_body['mouse_click']['right']['should_start'] = False
            response_body['mouse_click']['right']['should_cancel'] = True
            response_body['previous_finger_position']['x'] = fingers.index.position_in_frame.x
            response_body['previous_finger_position']['y'] = fingers.index.position_in_frame.y

            previous_finger_position = fingers.index.position_in_frame
        # Left click
        elif distance_index_to_middle <= configs.left_click_max_distance and distance_middle_to_ring > configs.right_click_max_distance:
            if configs.show_landmarkers:
                cv.line(frame, fingers.index.position_in_frame.to_list(), fingers.middle.position_in_frame.to_list(), (0, 0, 255), 2)

            if configs.show_delay_bar:
                draw_countdown(DrawCountdownOptions(
                    frame=frame,
                    center_point=fingers.index.position_in_frame.to_list(),
                    current_time=mouse_click_left['remaining_time'],
                    total_time=mouse_click_left['total_time'],
                ))

            response_body['mouse_move']['dx'] = 0
            response_body['mouse_move']['dy'] = 0
            response_body['mouse_click']['left']['remaining_time'] = mouse_click_left['remaining_time']
            response_body['mouse_click']['left']['total_time'] = mouse_click_left['total_time']
            response_body['mouse_click']['left']['should_start'] = True
            response_body['mouse_click']['left']['should_cancel'] = False
            response_body['mouse_click']['right']['remaining_time'] = 0
            response_body['mouse_click']['right']['total_time'] = 0
            response_body['mouse_click']['right']['should_start'] = False
            response_body['mouse_click']['right']['should_cancel'] = True
            response_body['previous_finger_position']['x'] = 0
            response_body['previous_finger_position']['y'] = 0
        # Right click
        elif distance_index_to_middle <= configs.left_click_max_distance and distance_middle_to_ring <= configs.right_click_max_distance:
            if configs.show_landmarkers:
                cv.line(frame, fingers.index.position_in_frame.to_list(), fingers.middle.position_in_frame.to_list(), (0, 0, 255), 2)
                cv.line(frame, fingers.middle.position_in_frame.to_list(), fingers.ring.position_in_frame.to_list(), (0, 0, 255), 2)

            if configs.show_delay_bar:
                draw_countdown(DrawCountdownOptions(
                    frame=frame,
                    center_point=fingers.index.position_in_frame.to_list(),
                    current_time=mouse_click_right['remaining_time'],
                    total_time=mouse_click_right['total_time'],
                ))

            response_body['mouse_move']['dx'] = 0
            response_body['mouse_move']['dy'] = 0
            response_body['mouse_click']['left']['remaining_time'] = 0
            response_body['mouse_click']['left']['total_time'] = 0
            response_body['mouse_click']['left']['should_start'] = False
            response_body['mouse_click']['left']['should_cancel'] = True
            response_body['mouse_click']['right']['remaining_time'] = mouse_click_right['remaining_time']
            response_body['mouse_click']['right']['total_time'] = mouse_click_right['total_time']
            response_body['mouse_click']['right']['should_start'] = True
            response_body['mouse_click']['right']['should_cancel'] = False
            response_body['previous_finger_position']['x'] = 0
            response_body['previous_finger_position']['y'] = 0
        else:
            response_body['mouse_move']['dx'] = 0
            response_body['mouse_move']['dy'] = 0
            response_body['mouse_click']['left']['remaining_time'] = 0
            response_body['mouse_click']['left']['total_time'] = 0
            response_body['mouse_click']['left']['should_start'] = False
            response_body['mouse_click']['left']['should_cancel'] = True
            response_body['mouse_click']['right']['remaining_time'] = 0
            response_body['mouse_click']['right']['total_time'] = 0
            response_body['mouse_click']['right']['should_start'] = False
            response_body['mouse_click']['right']['should_cancel'] = True
            response_body['previous_finger_position']['x'] = 0
            response_body['previous_finger_position']['y'] = 0


    _, image_encoded = cv.imencode('.jpg', frame)
    response_body['processed_image'] = image_encoded.tobytes()

    return Response(
        response=jsonpickle.encode(response_body),
        status=200,
        mimetype='application/json')


app.run(host='0.0.0.0', port=5000)

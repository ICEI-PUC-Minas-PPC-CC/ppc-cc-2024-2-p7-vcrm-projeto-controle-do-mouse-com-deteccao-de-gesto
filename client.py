import cv2 as cv
import jsonpickle
import numpy as np
from pynput.mouse import Button, Controller
import requests

from src.configs import Configs
from src.constants import EXIT_KEY_CODE, WEBCAM_INDEX
from src.countdown_timer import CountdownTimer
from src.vector import Vector


API_URL = 'http://localhost:5000'


def main():
    webcam = cv.VideoCapture(WEBCAM_INDEX)


    configs = Configs()
    previous_finger_position = Vector(0, 0)
    mouse_controller = Controller()
    left_click_countdown = CountdownTimer(configs.left_click_delay, lambda: mouse_controller.click(Button.left))
    right_click_countdown = CountdownTimer(configs.right_click_delay, lambda: mouse_controller.click(Button.right))


    while webcam.isOpened():
        status, frame = webcam.read()
        if not status or cv.waitKey(1) == EXIT_KEY_CODE:
            break


        _, image_encoded = cv.imencode('.jpg', frame)


        request_body = {
            'captured_image': image_encoded.tobytes(),
            'configs': {
                'cursor_sensitivity': configs.cursor_sensitivity,
                'left_click_max_distance': configs.left_click_max_distance,
                'left_click_delay': configs.left_click_delay,
                'right_click_max_distance': configs.right_click_max_distance,
                'right_click_delay': configs.right_click_delay,
                'show_landmarkers': configs.show_landmarkers,
                'show_delay_bar': configs.show_delay_bar,
            },
            'previous_finger_position': {
                'x': previous_finger_position.x,
                'y': previous_finger_position.y,
            },
            'mouse_click': {
                'left': {
                    'remaining_time': left_click_countdown.get_remaining_time(),
                    'total_time': left_click_countdown.get_total_time(),
                },
                'right': {
                    'remaining_time': right_click_countdown.get_remaining_time(),
                    'total_time': right_click_countdown.get_total_time(),
                },
            },
        }

        response = requests.post(
            API_URL,
            data=jsonpickle.encode(request_body),
            headers={'Content-Type': 'image/jpeg'})

        json = jsonpickle.decode(response.text)


        processed_image = json['processed_image']
        previous_finger_position = json['previous_finger_position']
        mouse_move = json['mouse_move']
        mouse_click_left = json['mouse_click']['left']
        mouse_click_right = json['mouse_click']['right']


        # Show processed image
        image_array = np.frombuffer(processed_image, np.uint8)
        frame = cv.imdecode(image_array, cv.IMREAD_COLOR)
        cv.imshow('Processed image', frame)

        # Update previous_finger_position
        previous_finger_position = Vector(previous_finger_position['x'], previous_finger_position['y'])

        # Move mouse
        if mouse_move['dx'] != 0 or mouse_move['dy'] != 0:
            mouse_controller.move(mouse_move['dx'], mouse_move['dy'])

        # Click left mouse
        if mouse_click_left['should_cancel']:
            left_click_countdown.stop()
        elif mouse_click_left['should_start']:
            left_click_countdown.start()

        # Click right mouse
        if mouse_click_right['should_cancel']:
            right_click_countdown.stop()
        elif mouse_click_right['should_start']:
            right_click_countdown.start()


if __name__ == '__main__':
    main()

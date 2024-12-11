import cv2 as cv
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode
from pynput.mouse import Button, Controller

from src.configs import Configs
from src.constants import MODEL_PATH, EXIT_KEY_CODE, WEBCAM_INDEX
from src.countdown_timer import CountdownTimer
from src.draw.countdown import DrawCountdownOptions, draw_countdown
from src.draw.landmarks import DrawLandmarksOptions, draw_landmarks
from src.fingers import Point, Fingers
from src.vector import Vector


def find_cameras():
    valid_indexes: list[str] = []

    for r in range(0, 10000):
        try:
            camera = cv.VideoCapture(r)
            if camera.isOpened():
                valid_indexes.append(str(r))
        except:
            pass

    if len(valid_indexes) > 0:
        print(f'Valid camera indexes found: "{", ".join(valid_indexes)}"')
    else:
        print('No valid camera indexes found')


def main():
    base_options = BaseOptions(model_asset_path=MODEL_PATH)
    hand_landmarker_options = HandLandmarkerOptions(
        base_options=base_options,
        running_mode=RunningMode.IMAGE)
    hand_landmarker = HandLandmarker.create_from_options(hand_landmarker_options)


    configs = Configs()
    webcam = cv.VideoCapture(WEBCAM_INDEX)
    frame_size = Vector(
        int(webcam.get(cv.CAP_PROP_FRAME_WIDTH)),
        int(webcam.get(cv.CAP_PROP_FRAME_HEIGHT))
    )

    previous_finger_position = Vector(0, 0)
    mouse_controller = Controller()
    left_click_countdown = CountdownTimer(configs.left_click_delay, lambda: mouse_controller.click(Button.left))
    right_click_countdown = CountdownTimer(configs.right_click_delay, lambda: mouse_controller.click(Button.right))


    while webcam.isOpened():
        status, frame = webcam.read()
        if not status or cv.waitKey(1) == EXIT_KEY_CODE:
            break


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

                mouse_controller.move(dx, dy)
                left_click_countdown.stop()
                right_click_countdown.stop()

                previous_finger_position = fingers.index.position_in_frame
            # Left click
            elif distance_index_to_middle <= configs.left_click_max_distance and distance_middle_to_ring > configs.right_click_max_distance:
                if configs.show_landmarkers:
                    cv.line(frame, fingers.index.position_in_frame.to_list(), fingers.middle.position_in_frame.to_list(), (0, 0, 255), 2)

                if configs.show_delay_bar:
                    draw_countdown(DrawCountdownOptions(
                        frame=frame,
                        center_point=fingers.index.position_in_frame.to_list(),
                        current_time=1000,
                        total_time=3000,
                    ))

                previous_finger_position = Vector(0, 0)
                left_click_countdown.stop()
                right_click_countdown.stop()
            # Right click
            elif distance_index_to_middle <= configs.left_click_max_distance and distance_middle_to_ring <= configs.right_click_max_distance:
                if configs.show_landmarkers:
                    cv.line(frame, fingers.index.position_in_frame.to_list(), fingers.middle.position_in_frame.to_list(), (0, 0, 255), 2)
                    cv.line(frame, fingers.middle.position_in_frame.to_list(), fingers.ring.position_in_frame.to_list(), (0, 0, 255), 2)

                if configs.show_delay_bar:
                    draw_countdown(DrawCountdownOptions(
                        frame=frame,
                        center_point=fingers.index.position_in_frame.to_list(),
                        current_time=1000,
                        total_time=3000,
                    ))

                previous_finger_position = Vector(0, 0)
                left_click_countdown.stop()
                right_click_countdown.stop()
            else:
                previous_finger_position = Vector(0, 0)
                left_click_countdown.stop()
                right_click_countdown.stop()

        cv.imshow('Camera', frame)


    webcam.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()

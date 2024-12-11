class Configs:
    def __init__(self):
        self.cursor_sensitivity = 1.0

        self.left_click_max_distance = 30
        self.left_click_delay = 3000

        self.right_click_max_distance = 30
        self.right_click_delay = 3000

        self.show_landmarkers = True
        self.show_delay_bar = True

    def from_dict(json: dict) -> 'Configs':
        configs = Configs()
        configs.cursor_sensitivity = json['cursor_sensitivity']
        configs.left_click_max_distance = json['left_click_max_distance']
        configs.left_click_delay = json['left_click_delay']
        configs.right_click_max_distance = json['right_click_max_distance']
        configs.right_click_delay = json['right_click_delay']
        configs.show_landmarkers = json['show_landmarkers']
        configs.show_delay_bar = json['show_delay_bar']
        return configs

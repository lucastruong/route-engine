from src.problem.problem_speed import ProblemSpeed, create_speed


def create_options(options: dict):
    speed = create_speed(options.get('traffic', 'normal'))
    balance = options.get('balance', False)
    polyline = options.get('polylines', False)
    mapbox = options.get('mapbox_key')
    max_running_time = options.get('max_running_time', 100)
    return ProblemOptions(speed, balance, polyline, mapbox, max_running_time)


class ProblemOptions:
    def __init__(self, speed: ProblemSpeed, balance: bool = False, polyline: bool = False,
                 mapbox: str = '', max_running_time: int = 2):
        self.speed = speed
        self.balance = balance
        self.polyline = polyline
        self.mapbox = mapbox
        self.max_running_time = max_running_time  # By minutes

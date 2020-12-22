from src.problem.problem_speed import ProblemSpeed, create_speed


def create_options(options: dict):
    speed = create_speed(options.get('traffic', 'normal'))
    balance = options.get('balance', False)
    polyline = options.get('polylines', False)
    mapbox = options.get('mapbox')
    return ProblemOptions(speed, balance, polyline, mapbox)


class ProblemOptions:
    def __init__(self, speed: ProblemSpeed, balance: bool = False, polyline: bool = False, mapbox: str = ''):
        self.speed = speed
        self.balance = balance
        self.polyline = polyline
        self.mapbox = mapbox

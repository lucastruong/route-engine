from src.problem.problem_speed import ProblemSpeed, create_speed


def create_options(options: dict):
    speed = create_speed(options.get('traffic', 'normal'))
    balance = options.get('balance', False)
    max_running_time = options.get('max_running_time', 2)
    max_iterations = options.get('max_iterations', 100)
    # For polyline
    polyline = options.get('polylines', False)
    mapbox = options.get('mapbox_key')
    graphhopper = options.get('graphhopper')
    osrm = options.get('osrm')

    return ProblemOptions(
        speed, balance,
        max_running_time, max_iterations,
        polyline, mapbox, graphhopper, osrm
    )


class ProblemOptions:
    def __init__(self, speed: ProblemSpeed, balance: bool = False,
                 max_running_time: int = 2, max_iterations: int = 100,
                 polyline: bool = False, mapbox: str = None, graphhopper: str = None, osrm: str = None,
                 ):
        self.speed = speed
        self.balance = balance
        self.max_running_time = max_running_time  # By minutes
        self.max_iterations = max_iterations  # By counter
        self.polyline = polyline
        self.mapbox = mapbox
        self.graphhopper = graphhopper
        self.osrm = osrm

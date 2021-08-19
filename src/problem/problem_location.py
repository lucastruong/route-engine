PROBLEM_LOCATION_VEHICLE = 'VEHICLE'
PROBLEM_LOCATION_PICKUP = 'PICKUP'
PROBLEM_LOCATION_DELIVERY = 'DELIVERY'


def create_problem_location(id_root, key, location: dict, location_type=PROBLEM_LOCATION_VEHICLE):
    return ProblemLocation(
        id_root, key,
        location.get('lat'), location.get('lng'),
        location_type,
    )


class ProblemLocation:
    def __init__(self, id_root: str, key: str, lat: float, lng: float, location_type: str):
        self.id_root = id_root
        self.id = key
        self.lat = float(lat)
        self.lng = float(lng)
        self.type = location_type
        # Data for solution
        self.time_window_start = 0
        self.time_window_end = 0
        self.distance = 0
        self.travel_time = 0
        self.service_time = 0
        self.waiting_time = 0
        # For time windows
        self.arrival_time = 0
        self.finish_time = 0

    def set_distance(self, distance):
        self.distance = distance  # By meter

    def set_travel_time(self, travel_time):
        self.travel_time = travel_time  # By seconds

    def set_service_time(self, service_time):
        self.service_time = service_time  # By seconds

    def set_waiting_time(self, waiting_time):
        self.waiting_time = waiting_time  # By seconds

    def set_arrival_time(self, arrival_time):
        self.arrival_time = arrival_time  # By seconds

    def set_finish_time(self, finish_time):
        self.finish_time = finish_time  # By seconds

    def set_time_window(self, start, end):
        self.time_window_start = start  # By seconds
        self.time_window_end = end  # By seconds

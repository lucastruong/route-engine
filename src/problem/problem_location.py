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

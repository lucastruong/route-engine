def create_problem_location(key, location: dict):
    return ProblemLocation(key, location.get('lat'), location.get('lng'))


class ProblemLocation:
    def __init__(self, key: str, lat: float, lng: float):
        self.id = key
        self.lat = float(lat)
        self.lng = float(lng)

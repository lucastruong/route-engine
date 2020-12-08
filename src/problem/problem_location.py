def create_problem_location(key, location: dict):
    name = location.get('name')
    if name is None:
        name = key
    return ProblemLocation(key, name, location.get('lat'), location.get('lng'))


class ProblemLocation:
    def __init__(self, key: str, name: str, lat: float, lng: float):
        self.id = key
        self.name = name
        self.lat = float(lat)
        self.lng = float(lng)

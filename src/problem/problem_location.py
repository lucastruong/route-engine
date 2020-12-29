def create_problem_location(id_root, key, location: dict):
    return ProblemLocation(
        id_root,
        key, location.get('lat'), location.get('lng')
    )


class ProblemLocation:
    def __init__(self, id_root: str, key: str, lat: float, lng: float):
        self.id_root = id_root
        self.id = key
        self.lat = float(lat)
        self.lng = float(lng)

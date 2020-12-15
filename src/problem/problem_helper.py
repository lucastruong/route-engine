from math import atan2, cos, radians, sin, sqrt

from src.problem.problem_location import ProblemLocation


def distance_two_points(start: ProblemLocation, end: ProblemLocation):
    """approximate radius of earth in km"""
    r = 6373.0

    lat1 = radians(start.lat)
    lon1 = radians(start.lng)
    lat2 = radians(end.lat)
    lon2 = radians(end.lng)

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    kilometers = r * c
    return kilometers


def kmph_to_mps(kmph):
    """Convert km/h to m/s"""
    base = 0.27777777777778
    return kmph * base

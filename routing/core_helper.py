from math import atan2, cos, radians, sin, sqrt

def distance_two_points(start, end):
    """approximate radius of earth in km"""
    R = 6373.0

    lat1 = radians(start.lat)
    lon1 = radians(start.lng)
    lat2 = radians(end.lat)
    lon2 = radians(end.lng)

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def kmph_to_mps(kmph):
    base = 0.27777777777778
    return kmph * base

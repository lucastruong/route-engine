import json
import urllib.request
from typing import List
from src.problem.problem_location import ProblemLocation
from polyline.codec import PolylineCodec

MAX_ELEMENTS_DIRECTIONS = 25


def send_request(locations: List[ProblemLocation], api_key):
    # Remove duplicates from list
    # coordinates = []
    # [coordinates.append(x) for x in visits if x not in coordinates]
    def build_address_str():
        address_str = ''
        for i in range(len(locations) - 1):
            address = locations[i]
            address_str += str(address.lng) + '%2C' + str(address.lat) + '%3B'
        address = locations[-1]
        address_str += str(address.lng) + '%2C' + str(address.lat)
        return address_str

    request = 'https://api.mapbox.com/directions/v5/mapbox/driving/'
    coordinates_str = build_address_str()
    request = request + coordinates_str + '?alternatives=false&geometries=polyline&steps=false&access_token=' + api_key
    json_result = urllib.request.urlopen(request).read()
    response = json.loads(json_result)
    route = response['routes'][0]
    geometry = route['geometry']

    # Modify distance and duration (travel time)
    distances = []
    travel_times = []
    legs = route['legs']
    for leg in legs:
        distances.append(int(leg.get('distance')))
        travel_times.append(int(leg.get('duration')))

    return {'geometry': geometry, 'distances': distances, 'travel_times': travel_times}


def send_request_step_by_step(locations: List[ProblemLocation], access_token: str):
    max_elements = MAX_ELEMENTS_DIRECTIONS
    num_addresses = len(locations)
    geometries = []
    distances = [0]
    travel_times = [0]

    def get_geometry(start_index, end_index):
        addresses = locations[start_index: end_index]
        request_response = send_request(addresses, access_token)
        return request_response

    i = 0
    while i < num_addresses - 1:
        start = i
        end = start + max_elements
        response = get_geometry(start, end)
        geometries.append(response.get('geometry'))

        # For distances and durations
        distances += response.get('distances')
        travel_times += response.get('travel_times')

        i += max_elements - 1

    return {'geometries': geometries, 'distances': distances, 'travel_times': travel_times}


def mapbox_directions(locations: List[ProblemLocation], access_token: str):
    if len(locations) < 2:
        return None

    result = send_request_step_by_step(locations, access_token)
    distances = result.get('distances')
    travel_times = result.get('travel_times')
    geometries = result.get('geometries')

    polyline = []
    for geometry in geometries:
        decoding = PolylineCodec().decode(geometry)
        polyline += decoding

    geometry = PolylineCodec().encode(polyline)

    return {'geometry': geometry, 'distances': distances, 'travel_times': travel_times}

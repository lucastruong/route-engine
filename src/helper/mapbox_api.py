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
    geometry = response['routes'][0]['geometry']
    return {'geometry': geometry}


def send_request_step_by_step(locations: List[ProblemLocation], access_token: str):
    max_elements = MAX_ELEMENTS_DIRECTIONS
    num_addresses = len(locations)
    geometries = []

    def get_geometry(start_index, end_index):
        addresses = locations[start_index: end_index]
        response = send_request(addresses, access_token)
        return response.get('geometry')

    i = 0
    while i < num_addresses - 1:
        start = i
        end = start + max_elements
        geometry = get_geometry(start, end)
        geometries.append(geometry)
        i += max_elements - 1

    return geometries


def mapbox_directions(locations: List[ProblemLocation], access_token: str):
    if len(locations) < 2:
        return None

    geometries = send_request_step_by_step(locations, access_token)
    polyline = []
    for geometry in geometries:
        decoding = PolylineCodec().decode(geometry)
        polyline += decoding

    geometry = PolylineCodec().encode(polyline)

    return geometry

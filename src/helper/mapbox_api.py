import json
import urllib
from src.problem.problem_location import ProblemLocation
from polyline.codec import PolylineCodec


MAX_ELEMENTS_DIRECTIONS = 25

def send_request(locations: list[ProblemLocation], api_key):
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


def send_request_step_by_step(locations: list[ProblemLocation], access_token: str):
    max_elements = MAX_ELEMENTS_DIRECTIONS
    num_addresses = len(locations)
    max_rows = max_elements
    q, r = divmod(num_addresses, max_rows)
    geometries = []

    def get_geometry(start, end):
        addresses = locations[start: end]
        response = send_request(addresses, access_token)
        return response.get('geometry')

    # Send q requests, returning max_rows rows per request.
    for i in range(q):
        geometry = get_geometry(i * max_rows, (i + 1) * max_rows)
        geometries.append(geometry)

    # Get the remaining remaining r rows, if necessary.
    if r > 0:
        geometry = get_geometry(q * max_rows, q * max_rows + r)
        geometries.append(geometry)

    return geometries


def mapbox_directions(locations: list[ProblemLocation], access_token: str):
    geometries = send_request_step_by_step(locations, access_token)
    polyline = []
    for geometry in geometries:
        decoding = PolylineCodec().decode(geometry)
        polyline += decoding

    geometry = PolylineCodec().encode(polyline)

    return geometry

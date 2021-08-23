from typing import List
import json
import urllib.request
from polyline.codec import PolylineCodec

from src.problem.problem_location import ProblemLocation


class ProblemPolyline:
    def __init__(self, locations: List[ProblemLocation], mapbox_key: str = '', graphhopper: str = '', osrm: str = ''):
        self.max_elements = 25
        self.locations = locations
        self.mapbox_key = mapbox_key
        self.graphhopper_url = graphhopper
        self.osrm_url = osrm
        self.service = 'MAPBOX'  # Default mapbox
        self.service = 'GRAPHHOPPER' if graphhopper is not None else self.service
        self.service = 'OSRM' if osrm is not None else self.service

    def send_request(self, addresses):
        if self.service == 'MAPBOX':
            return mapbox_send_request(addresses, self.mapbox_key)
        if self.service == 'GRAPHHOPPER':
            return graphhopper_send_request(addresses, self.graphhopper_url)
        if self.service == 'OSRM':
            return osrm_send_request(addresses, self.osrm_url)

    def send_request_step_by_step(self):
        max_elements = self.max_elements
        locations = self.locations
        num_addresses = len(locations)
        geometries = []
        distances = [0]
        travel_times = [0]

        def get_geometry(start_index, end_index):
            addresses = locations[start_index: end_index]
            request_response = self.send_request(addresses)
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

    def directions(self):
        if len(self.locations) < 2:
            return None

        result = self.send_request_step_by_step()
        distances = result.get('distances')
        travel_times = result.get('travel_times')
        geometries = result.get('geometries')

        polyline = []
        for geometry in geometries:
            decoding = PolylineCodec().decode(geometry)
            polyline += decoding

        geometry = PolylineCodec().encode(polyline)

        return {'geometry': geometry, 'distances': distances, 'travel_times': travel_times}


def mapbox_send_request(locations: List[ProblemLocation], api_key):
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


def graphhopper_send_request(locations: List[ProblemLocation], graphhopper_url):
    def build_address_str():
        address_str = ''
        for i in range(len(locations) - 1):
            address = locations[i]
            address_str += 'point=' + str(address.lat) + ',' + str(address.lng) + '&'
        address = locations[-1]
        address_str += 'point=' + str(address.lat) + ',' + str(address.lng)
        return address_str

    coordinates_str = build_address_str()
    request = graphhopper_url + '?' + coordinates_str
    json_result = urllib.request.urlopen(request).read()
    response = json.loads(json_result)
    geometry = response['paths'][0]['points']

    return {'geometry': geometry, 'distances': [], 'travel_times': []}


def osrm_send_request(locations: List[ProblemLocation], osrm_url):
    def build_address_str():
        address_str = ''
        for i in range(len(locations) - 1):
            address = locations[i]
            address_str += str(address.lng) + ',' + str(address.lat) + ';'
        address = locations[-1]
        address_str += str(address.lng) + ',' + str(address.lat)
        return address_str

    coordinates_str = build_address_str()
    request = osrm_url + '/driving/' + coordinates_str
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

from typing import List

from src.problem.problem_helper import seconds_to_hhmm
from src.problem.problem_location import ProblemLocation
from src.problem.problem_vehicle import ProblemVehicle


def cal_time_for_location(location: ProblemLocation, start_seconds, distance, speed):
    location.set_distance(distance)
    location.set_travel_time(int(location.distance / speed))
    arrival_time = start_seconds + location.travel_time
    location.set_waiting_time(
        0 if arrival_time > location.time_window_start else location.time_window_start - arrival_time)
    location.set_arrival_time(arrival_time + location.waiting_time)
    location.set_finish_time(location.arrival_time + location.service_time)
    return location


class ProblemSolution:
    def __init__(self, vehicles: List[ProblemVehicle], locations: List[ProblemLocation], distance_matrix, service_times):
        self.vehicles = vehicles
        self.locations = locations
        self.distance_matrix = distance_matrix
        self.service_times = service_times
        # Data of solution
        self.unserved = []
        self.routes = {}

    def set_unserved(self, unserved=[]):
        self.unserved = unserved

    def set_routes(self, routes=[]):
        visits = {}
        for i, route in enumerate(routes):
            steps = []
            pre_index = route[0]
            vehicle = self.vehicles[i]
            vehicle_speed = vehicle.speed.mps
            start_seconds = vehicle.start_time.seconds

            for index in route:
                location = self.locations[index]
                distance = self.distance_matrix[pre_index][index]
                location = cal_time_for_location(location, start_seconds, distance, vehicle_speed)
                # Repaired for next
                steps.append(location)
                pre_index = index
                start_seconds = location.finish_time

            if len(steps) == 2 and steps[0].id_root == steps[1].id_root:
                steps = []

            if len(steps) == 1:
                steps = []

            # Add new a route for vehicle
            visits[vehicle.id] = {
                'steps': steps,
                'speed': vehicle_speed,  # To meters per seconds
            }
        self.routes = visits

    def modify_distances(self, geometries, distances):
        if len(geometries) <= 0:
            return

        i = 0
        for vehicle_id_root, vehicle_route in self.routes.items():
            locations = vehicle_route.get('steps')
            if len(locations) <= 0:
                continue

            self.routes[vehicle_id_root]['geometry'] = geometries[i]

            # Skip it when not have distances
            route_distance = distances[i]
            if len(route_distance) <= 1:
                continue

            vehicle_speed = vehicle_route.get('speed')
            vehicle_location = locations[0]
            start_seconds = vehicle_location.time_window_start

            for idx, location in enumerate(locations):
                distance = route_distance[idx]
                location = cal_time_for_location(location, start_seconds, distance, vehicle_speed)
                # Repaired for next
                start_seconds = location.finish_time

            i += 1

    def get_times(self):
        time_windows = []
        travel_times = []
        service_times = []
        waiting_times = []
        distances = []
        ids = []

        for vehicle_route in self.routes.values():
            route = vehicle_route.get('steps')
            route_time_window = []
            route_travel_time = []
            route_service_time = []
            route_waiting_time = []
            route_distance = []
            route_ids = []

            for location in route:
                start = seconds_to_hhmm(location.arrival_time)
                end = seconds_to_hhmm(location.finish_time)
                route_time_window.append((start, end))
                route_travel_time.append(location.travel_time)
                route_service_time.append(location.service_time)
                route_waiting_time.append(location.waiting_time)
                route_distance.append(location.distance)
                route_ids.append(location.id)

            time_windows.append(route_time_window)
            travel_times.append(route_travel_time)
            service_times.append(route_service_time)
            waiting_times.append(route_waiting_time)
            distances.append(route_distance)
            ids.append(route_ids)

        return {
            'time_windows': time_windows,
            'travel_times': travel_times,
            'service_times': service_times,
            'waiting_times': waiting_times,
            'distances': distances,
            'ids': ids,
        }

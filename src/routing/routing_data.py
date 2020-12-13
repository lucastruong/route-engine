import sys

from src.problem.problem_adapter import ProblemAdapter
from src.problem.problem_helper import distance_two_points
from src.problem.problem_location import ProblemLocation, create_problem_location
from src.problem.problem_time import ProblemTime


def create_data_locations(adapter: ProblemAdapter):
    locations = []
    times = []
    service_times = []
    starts = []
    ends = []

    # Allowing arbitrary start and end locations
    # depot_location = create_problem_location('depot', {'lat': 0, 'lng': 0})
    # locations.append(depot_location)

    for vehicle in adapter.vehicles:
        locations.append(vehicle.location)
        starts.append(len(locations) - 1)

        if vehicle.end_location is not None:
            locations.append(vehicle.end_location)
        ends.append(len(locations) - 1)

        times.append((vehicle.start_time, vehicle.end_time))
        service_times.append(0)

    for visit in adapter.visits:
        locations.append(visit.location)
        times.append((visit.start_time, visit.end_time))
        service_times.append(visit.duration.seconds)

    return {
        'locations': locations, 'starts': starts, 'ends': ends,
        'times': times, 'service_times': service_times
    }


def create_data_capacities(adapter: ProblemAdapter):
    # Prepare the capacities global
    capacities = []

    for vehicle in adapter.vehicles:
        for capacity_key in vehicle.capacities.demands:
            if capacity_key not in capacities:
                capacities.append(capacity_key)
        for skill_key in vehicle.skills.demands:
            if skill_key not in capacities:
                capacities.append(skill_key)

    for visit in adapter.visits:
        for capacity_key in visit.loads.demands:
            if capacity_key not in capacities:
                capacities.append(capacity_key)
        for skill_key in visit.required_skills.demands:
            if skill_key not in capacities:
                capacities.append(skill_key)

    # Prepare the capacities of vehicles
    demands = {}
    vehicle_capacities = {}
    for capacity_key in capacities:
        sub_demands = []
        # sub_demands.append(0)  # For depot
        sub_vehicle_capacities = []

        for vehicle in adapter.vehicles:
            sub_demands.append(0)
            if vehicle.end_location is not None:
                sub_demands.append(0)

            if capacity_key in vehicle.capacities.demands:
                sub_vehicle_capacities.append(vehicle.capacities.demands.get(capacity_key))
            elif capacity_key in vehicle.skills.demands:
                sub_vehicle_capacities.append(sys.maxsize)
            else:
                sub_vehicle_capacities.append(0)

        for visit in adapter.visits:
            if capacity_key in visit.loads.demands:
                sub_demands.append(visit.loads.demands.get(capacity_key))
            elif capacity_key in visit.required_skills.demands:
                sub_demands.append(1)
            else:
                sub_demands.append(0)

        demands[capacity_key] = sub_demands
        vehicle_capacities[capacity_key] = sub_vehicle_capacities

    # 'capacities' = {list: 4}['CAP_WEIGHT', 'CAP_VOLUME', 'SKILL_A', 'SKILL_B']
    # 'demands' = {dict: 4}
    # {'CAP_WEIGHT': [0, 1, 3, 3, 1], 'CAP_VOLUME': [0, 2, 4, 6, 8], 'SKILL_A': [0, 0, 1, 0, 0],
    #  'SKILL_B': [0, 0, 1, 0, 0]}
    # 'vehicle_capacities' = {dict: 4}
    # {'CAP_WEIGHT': [20], 'CAP_VOLUME': [20], 'SKILL_A': [9223372036854775807], 'SKILL_B': [9223372036854775807]}
    return {'capacities': capacities, 'demands': demands, 'vehicle_capacities': vehicle_capacities}


def compute_data_matrix(locations: list[ProblemLocation], speed=30):
    """Creates callback to return time between points."""
    distances = {}
    times = {}
    for from_counter, from_node in enumerate(locations):
        distances[from_counter] = {}
        times[from_counter] = {}
        for to_counter, to_node in enumerate(locations):
            if from_counter == to_counter or from_node.id == 'depot' or to_node.id == 'depot':
                distances[from_counter][to_counter] = 0
                times[from_counter][to_counter] = 0
            else:
                distance_km = distance_two_points(from_node, to_node)
                speed_hour = speed  # 30km/h
                time_hour = distance_km / speed_hour
                times[from_counter][to_counter] = int(time_hour * 60 * 60)  # To seconds
                distances[from_counter][to_counter] = int(distance_km * 1000)  # To meters

    time_matrix = []
    for times_sub in times.values():
        time_matrix_sub = []
        for time_value in times_sub.values():
            time_matrix_sub.append(time_value)
        time_matrix.append(time_matrix_sub)

    return {'distances': distances, 'times': time_matrix}


def compute_time_windows(times: list[tuple[ProblemTime, ProblemTime]]):
    windows = []
    for counter, node in enumerate(times):
        start_time = node[0]
        end_time = node[1]
        windows.append((start_time.seconds, end_time.seconds))
    return windows

import sys
from typing import List, Tuple
from src.problem.problem_adapter import ProblemAdapter
from src.problem.problem_helper import distance_two_points
from src.problem.problem_location import ProblemLocation, create_problem_location
from src.problem.problem_time import ProblemTime


def create_data_locations(adapter: ProblemAdapter):
    locations = []
    location_ids = []
    times = []
    service_times = []
    starts = []
    ends = []
    pickups_deliveries = []
    start_time = ProblemTime('00:00')
    end_time = ProblemTime('999:999')
    force_order = False

    def push_data(location, time, service_time):
        locations.append(location)
        location_ids.append(location.id)
        times.append(time)
        service_times.append(service_time)

    def push_pickups_deliveries(pickup_index, delivery_index):
        pickups_deliveries.append([pickup_index, delivery_index])

    # Allowing arbitrary start and end locations
    virtual_depot = create_problem_location('virtual_depot', 'virtual_depot', {'lat': 0, 'lng': 0})
    push_data(virtual_depot, (start_time, end_time), 0)
    virtual_depot_index = 0

    for vehicle in adapter.vehicles:
        push_data(vehicle.location, (vehicle.start_time, vehicle.end_time), 0)
        starts.append(len(locations) - 1)

        if vehicle.end_location is not None:
            push_data(vehicle.end_location, (start_time, end_time), 0)
            ends.append(len(locations) - 1)
        else:
            ends.append(0)  # End as virtual_depot

    for visit in adapter.visits:
        push_data(visit.location, (visit.start_time, visit.end_time), visit.duration.seconds)

    # For vehicle orders
    for vehicle in adapter.vehicles:
        for order_index in range(len(vehicle.order) - 1):
            force_order = True
            orders = vehicle.order
            start_location_index = location_ids.index(orders[order_index])
            end_location_index = location_ids.index(orders[order_index + 1])
            push_pickups_deliveries(start_location_index, end_location_index)

    return {
        'virtual_depot_index': virtual_depot_index,
        'locations': locations, 'starts': starts, 'ends': ends,
        'service_times': service_times,
        'times': times,
        'pickups_deliveries': pickups_deliveries, 'force_order': force_order
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
        sub_demands = [0]  # 0: For depot
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

    # 'capacities' = {list: 2} ['CAP_WEIGHT', 'SKILL_A']
    # 'demands' = {dict: 2} {'CAP_WEIGHT': [0, 1, 3, 3, 1], 'SKILL_A': [0, 0, 1, 0, 0]}
    # 'vehicle_capacities' = {dict: 2} {'CAP_WEIGHT': [20], 'SKILL_A': [9223372036854775807]}
    return {'capacities': capacities, 'demands': demands, 'vehicle_capacities': vehicle_capacities}


def compute_data_matrix(locations: List[ProblemLocation]):
    """Creates callback to return time between points."""
    distance_matrix = {}
    for from_counter, from_node in enumerate(locations):
        distance_matrix[from_counter] = {}
        for to_counter, to_node in enumerate(locations):
            if from_counter == to_counter or from_node.id == 'virtual_depot' or to_node.id == 'virtual_depot':
                distance_matrix[from_counter][to_counter] = 0
            else:
                distance_km = distance_two_points(from_node, to_node)
                distance_meters = int(distance_km * 1000)  # To meters
                distance_matrix[from_counter][to_counter] = distance_meters
    return distance_matrix


def compute_time_windows(times: List[Tuple[ProblemTime, ProblemTime]]):
    windows = []
    for counter, node in enumerate(times):
        start_time = node[0]
        end_time = node[1]
        windows.append((start_time.seconds, end_time.seconds))
    return windows

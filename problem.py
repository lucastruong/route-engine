import datetime
import json
import os
import sys
import time
from functools import partial
from pprint import pprint

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from src.problem.problem_adapter import ProblemAdapter
from src.routing.routing_constraints import add_distance_constraint, add_capacities_constraint, allow_drop_nodes, \
    add_time_windows_constraints
from src.routing.routing_data import create_data_locations, create_data_capacities, compute_data_matrix, \
    compute_time_windows
from src.routing.routing_solution import format_solution


def read_in():
    lines = sys.stdin.readlines()
    # Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])


def read_problem_json():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    f = open(dir_path + "/data/problem.json", "r")
    json_obj = json.loads(f.read())
    f.close()
    # Get our data as an array from read_in()
    # json_obj = read_in()
    return json_obj


def prepare_adapter(problem_json):
    """Format problem"""
    adapter = ProblemAdapter(problem_json)
    adapter.transform_routific()
    return adapter


def create_data_model(problem_json):
    adapter = prepare_adapter(problem_json)
    data = create_data_locations(adapter)
    locations = data.get('locations')
    distance_matrix = compute_data_matrix(locations)

    """Stores the data for the problem."""
    data['locations'] = locations
    data['distance_matrix'] = distance_matrix
    data['num_vehicles'] = len(adapter.vehicles)

    # Start and end locations for routes
    starts = data.get('starts')
    ends = data.get('ends')
    data['starts'] = starts
    data['ends'] = ends

    # Capacity constraint.
    capacities = create_data_capacities(adapter)
    data['capacities'] = capacities.get('capacities')
    data['demands'] = capacities.get('demands')
    data['vehicle_capacities'] = capacities.get('vehicle_capacities')

    # Time Window constraint.
    data['vehicle_speed'] = adapter.options.speed.mps  # Travel speed: meters/seconds
    data['service_times'] = data.get('service_times')
    data['time_windows'] = compute_time_windows(data.get('times'))
    data['num_locations'] = len(data['locations'])

    # TMP
    data['adapter'] = adapter
    data['global_span'] = 100
    data['num_visits'] = len(adapter.visits)

    # The time required to load a vehicle
    data['vehicle_load_time'] = 1800
    # The time required to unload a vehicle.
    data['vehicle_unload_time'] = 1800
    # The maximum number of vehicles that can load or unload at the same time.
    data['depot_capacity'] = 1

    return data


def create_time_evaluator(data):
    """Creates callback to get total times between locations."""

    def service_time(from_node):
        """Gets the service time for the specified location."""
        return data['service_times'][from_node]

    def travel_time(from_node, to_node):
        """Gets the travel times between two locations."""
        travel_time_from_to = 0
        if from_node != to_node:
            travel_time_from_to = int(data['distance_matrix'][from_node][to_node] / data['vehicle_speed'])
        return travel_time_from_to

    def time_evaluator(manager, from_node, to_node):
        """Returns the total time between the two nodes"""
        from_index = manager.IndexToNode(from_node)
        to_index = manager.IndexToNode(to_node)
        return travel_time(from_index, to_index) + service_time(from_index)

    return time_evaluator


def create_distance_evaluator(data):
    """Creates callback to return distance between points."""
    distance_matrix = data['distance_matrix']

    def distance_evaluator(manager, from_node, to_node):
        """Returns the manhattan distance between the two nodes"""
        return distance_matrix[manager.IndexToNode(from_node)][manager.IndexToNode(
            to_node)]

    return distance_evaluator


def main(problem_json):
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_data_model(problem_json)
    pprint(data['vehicle_speed'])
    pprint(data['service_times'])

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'],
                                           data['starts'], data['ends'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Define weight of each edge
    distance_evaluator_index = routing.RegisterTransitCallback(partial(create_distance_evaluator(data), manager))
    routing.SetArcCostEvaluatorOfAllVehicles(distance_evaluator_index)

    # Add Distance constraint.
    add_distance_constraint(routing, distance_evaluator_index)

    # Creates capacities constraints for each vehicle.
    add_capacities_constraint(routing, manager, data)

    # Add Time Window constraint
    time_evaluator_index = routing.RegisterTransitCallback(partial(create_time_evaluator(data), manager))
    add_time_windows_constraints(routing, manager, data, time_evaluator_index)

    # Allow to drop nodes.
    allow_drop_nodes(routing, manager, data)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if assignment:
        return format_solution(data, manager, routing, assignment)
    else:
        print('No solution found!')


if __name__ == '__main__':
    start_time = time.time()
    print("--- ROUTE-ENGINE: ---")
    main()
    end_time = int(time.time() - start_time)
    end_time = str(datetime.timedelta(seconds=end_time))
    print("--- END: %s ---" % end_time)

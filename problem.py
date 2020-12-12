import datetime
import json
import os
import sys
import time
from functools import partial

from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from six.moves import xrange

from src.problem.problem_adapter import ProblemAdapter
from src.routing.routing_constraints import add_distance_constraint, add_capacities_constraint, allow_drop_nodes
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
    starts = data.get('starts')
    ends = data.get('ends')
    matrix = compute_data_matrix(locations, adapter.options.speed)

    times = data.get('times')
    service_times = data.get('service_times')
    capacities = create_data_capacities(adapter)
    time_windows = compute_time_windows(times)

    """Stores the data for the problem."""
    data['locations'] = locations
    data['distance_matrix'] = matrix.get('distances')
    data['num_vehicles'] = len(adapter.vehicles)
    data['starts'] = starts
    data['ends'] = ends

    data['adapter'] = adapter
    data['time_matrix'] = matrix.get('times')
    data['time_windows'] = time_windows
    data['service_times'] = service_times

    # Capacity constraint.
    data['capacities'] = capacities.get('capacities')
    data['demands'] = capacities.get('demands')
    data['vehicle_capacities'] = capacities.get('vehicle_capacities')
    # End capacity constraint.

    data['global_span'] = 100
    data['num_locations'] = len(data['locations'])
    data['num_visits'] = len(adapter.visits)

    # The time required to load a vehicle
    data['vehicle_load_time'] = 1800
    # The time required to unload a vehicle.
    data['vehicle_unload_time'] = 1800
    # The maximum number of vehicles that can load or unload at the same time.
    data['depot_capacity'] = 1

    return data


def add_distance_dimension(routing, distance_evaluator_index, data):
    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        distance_evaluator_index,
        0,  # no slack
        100 * 1000,  # vehicle maximum travel distance, maximum distance per vehicle
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    # Try to minimize the max distance among vehicles.
    # /!\ It doesn't mean the standard deviation is minimized
    # distance_dimension.SetGlobalSpanCostCoefficient(data['global_span'])


def create_time_evaluator(data):
    """Creates callback to get total times between locations."""

    def service_time(data, node):
        """Gets the service time for the specified location."""
        return data['service_times'][node]

    def travel_time(data, from_node, to_node):
        """Gets the travel times between two locations."""
        if from_node == to_node:
            travel_time = 0
        else:
            travel_time = data['time_matrix'][from_node][to_node]
        return travel_time

    _total_time = {}
    # precompute total time to have time callback in O(1)
    for from_node in xrange(data['num_locations']):
        _total_time[from_node] = {}
        for to_node in xrange(data['num_locations']):
            if from_node == to_node:
                _total_time[from_node][to_node] = 0
            else:
                _total_time[from_node][to_node] = int(
                    service_time(data, from_node) + travel_time(data, from_node, to_node))

    def time_evaluator(manager, from_node, to_node):
        """Returns the total time between the two nodes"""
        return _total_time[manager.IndexToNode(from_node)][manager.IndexToNode(to_node)]

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

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']), data['num_vehicles'],
                                           data['starts'], data['ends'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    distance_evaluator_index = routing.RegisterTransitCallback(partial(create_distance_evaluator(data), manager))
    routing.SetArcCostEvaluatorOfAllVehicles(distance_evaluator_index)

    # Add Distance constraint.
    add_distance_constraint(routing, distance_evaluator_index)

    # Creates capacities constraints for each vehicle.
    add_capacities_constraint(routing, manager, data)

    # Allow to drop nodes.
    allow_drop_nodes(routing, manager, data)

    # Register time callback
    # transit_callback_index = routing.RegisterTransitCallback(partial(create_time_evaluator(data), manager))

    # Add Time constraint.
    # add_time_window_constraints(routing, manager, data, transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)

    return format_solution(data, manager, routing, assignment)

    # # Print solution on console.
    # if assignment:
    #     format_solution(data, manager, routing, assignment)
    # else:
    #     print('No solution found!')


if __name__ == '__main__':
    start_time = time.time()
    print("--- ROUTE-ENGINE: ---")
    main()
    end_time = int(time.time() - start_time)
    end_time = str(datetime.timedelta(seconds=end_time))
    print("--- END: %s ---" % end_time)

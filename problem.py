import datetime
import json
import os
import sys
import time
from functools import partial
from pprint import pprint

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from src.helper.measure_decorator import measure
from src.problem.problem_adapter import ProblemAdapter
from src.routing.routing_constraints import add_distance_constraint, add_capacities_constraint, allow_drop_nodes, \
    add_time_windows_constraints, add_counter_constraints, add_pickups_deliveries_constraints
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

    # Pickups and Deliveries
    data['pickups_deliveries'] = data.get('pickups_deliveries')

    # Options
    data['balance'] = adapter.options.balance
    data['num_visits'] = len(adapter.visits)

    # Mapbox
    data['polyline'] = adapter.options.polyline
    data['mapbox'] = adapter.options.mapbox

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

    def time_evaluator(manager, from_index, to_index):
        """Returns the total time between the two nodes"""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return travel_time(from_node, to_node) + service_time(to_node)

    return time_evaluator


def create_distance_evaluator(data):
    """Creates callback to return distance between points."""
    distance_matrix = data['distance_matrix']

    def distance_evaluator(manager, from_node, to_node):
        """Returns the manhattan distance between the two nodes"""
        return distance_matrix[manager.IndexToNode(from_node)][manager.IndexToNode(
            to_node)]

    return distance_evaluator


def create_counter_evaluator(data):
    starts = data['starts']
    ends = data['ends']

    def counter_callback(manager, from_index):
        """Returns 1 for any locations except depot."""
        # Convert from routing variable Index to user NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return 0 if (from_node in starts or from_node in ends) else 1

    return counter_callback


@measure
def main(problem_json):
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_data_model(problem_json)
    pprint(data['distance_matrix'])

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

    # Add Time Window constraint.
    time_evaluator_index = routing.RegisterTransitCallback(partial(create_time_evaluator(data), manager))
    add_time_windows_constraints(routing, manager, data, time_evaluator_index)

    # Balance constraint.
    counter_evaluator_index = routing.RegisterUnaryTransitCallback(partial(create_counter_evaluator(data), manager))
    add_counter_constraints(routing, data, counter_evaluator_index)

    # Define Transportation Requests.
    add_pickups_deliveries_constraints(routing, manager, data)

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

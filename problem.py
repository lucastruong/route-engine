from core_object import Problem_Adapter
from core_helper import distance_two_points
from core_data import create_data_all_locations, create_data_locations, create_data_times, create_data_capacities, create_data_service_times

import traceback, time, datetime, json
from functools import partial
from six.moves import xrange

from ortools.constraint_solver import pywrapcp, routing_enums_pb2
import os, sys, requests

def read_in():
    lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])

def read_problem_json():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    f = open(dir_path + "/data/example.json", "r")
    json_obj = json.loads(f.read())
    f.close()

    # Get our data as an array from read_in()
    # json_obj = read_in()
    return json_obj

def prepare_adapter():
    """Read problem json"""
    problem = read_problem_json()

    """Format problem"""
    adapter = Problem_Adapter(problem)
    adapter.transform_routific()
    return adapter

def compute_time_matrix(locations):
    """Creates callback to return time between points."""
    distances = {}
    times = {}
    for from_counter, from_node in enumerate(locations):
        distances[from_counter] = {}
        times[from_counter] = {}
        for to_counter, to_node in enumerate(locations):
            if from_counter == to_counter:
                distances[from_counter][to_counter] = 0
                times[from_counter][to_counter] = 0
            else:
                distance_km = distance_two_points(from_node, to_node)
                speed_hour = 40; # 40km/h
                time_hour = distance_km / speed_hour
                times[from_counter][to_counter] = int(time_hour * 60 * 60)  # To seconds
                distances[from_counter][to_counter] = distance_km * 1000  # To meters

    time_matrix = []
    for times_sub in times.values():
        time_matrix_sub = []
        for time_value in times_sub.values():
            time_matrix_sub.append(time_value)
        time_matrix.append(time_matrix_sub)

    return {'distances': distances, 'times': time_matrix}

def compute_time_windows(times):
    windows = []
    for counter, node in enumerate(times):
        start_time = node[0]
        end_time = node[1]
        windows.append((start_time.seconds, end_time.seconds))
    return windows
    
def create_data_model():
    adapter = prepare_adapter()
    locations = create_data_locations(adapter)
    times = create_data_times(adapter)
    capacities = create_data_capacities(adapter)
    matrix = compute_time_matrix(locations)
    service_times = create_data_service_times(adapter)

    """Stores the data for the problem."""
    data = {}
    data['adapter'] = adapter
    data['distance_matrix'] = matrix.get('distances')
    data['time_matrix'] = matrix.get('times')
    data['time_windows'] = compute_time_windows(times)
    data['service_times'] = service_times

    data['capacities'] = capacities.get('capacities')
    data['demands'] = capacities.get('demands')
    data['vehicle_capacities'] = capacities.get('vehicle_capacities')
    data['global_span'] = 100

    data['locations'] = create_data_all_locations(adapter)
    data['num_locations'] = len(data['locations'])
    data['num_visits'] = len(adapter.visits)
    data['num_vehicles'] = len(adapter.vehicles)
    data['starts'] = []
    data['ends'] = []
    for i in range(data['num_vehicles']):
        data['starts'].append(i)
        data['ends'].append(i)

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

def create_demand_callback(demands):
    # Add Capacity constraint.
    def demand_callback(manager, from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    return demand_callback

def add_capacities_constraints(routing, manager, data):
    capacities = data['capacities']
    demands = data['demands']
    vehicle_capacities = data['vehicle_capacities']

    for capacity_key in capacities:
        sub_demands = demands.get(capacity_key)
        sub_vehicle_capacities = vehicle_capacities.get(capacity_key)

        demand_callback_index = routing.RegisterUnaryTransitCallback(
            partial(create_demand_callback(sub_demands), manager))

        capacity = 'Capacity' + capacity_key
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            sub_vehicle_capacities,  # vehicle maximum capacities
            True,  # start cumul to zero
            capacity)

def allow_drop_visits(routing, manager, data):
    # Allow to drop nodes.
    penalty = 10000
    for node in range(1, len(data['time_matrix'])):
        index = manager.NodeToIndex(node)
        routing.AddDisjunction([index], penalty)

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
                _total_time[from_node][to_node] = int(service_time(data, from_node) + travel_time(data, from_node, to_node))

    def time_evaluator(manager, from_node, to_node):
        """Returns the total time between the two nodes"""
        return _total_time[manager.IndexToNode(from_node)][manager.IndexToNode(to_node)]

    return time_evaluator

def add_time_window_constraints(routing, manager, data, time_evaluator_index):
    dimension_name = 'Time'
    routing.AddDimension(
        time_evaluator_index,
        24 * 60 * 60,  # allow waiting time
        24 * 60 * 60,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        dimension_name)
    time_dimension = routing.GetDimensionOrDie(dimension_name)

    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx < data['num_vehicles']:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add time window constraints for each vehicle start node.
    for vehicle_id in range(data['num_vehicles']):
        # Add time windows at start of routes
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(data['time_windows'][vehicle_id][0],
                                                data['time_windows'][vehicle_id][1])

    # Add resource constraints at the depot.
    # solver = routing.solver()
    # intervals = []
    # for i in range(data['num_vehicles']):
    #     # Add time windows at start of routes
    #     intervals.append(
    #         solver.FixedDurationIntervalVar(
    #             time_dimension.CumulVar(routing.Start(i)),
    #             data['vehicle_load_time'], 'depot_interval'))
    #     # Add time windows at end of routes.
    #     intervals.append(
    #         solver.FixedDurationIntervalVar(
    #             time_dimension.CumulVar(routing.End(i)),
    #             data['vehicle_unload_time'], 'depot_interval'))

    # depot_usage = [1 for i in range(len(intervals))]
    # solver.Add(
    #     solver.Cumulative(intervals, depot_usage, data['depot_capacity'],
    #                       'depot'))

    # Instantiate route start and end times to produce feasible times.
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))

def get_routes(manager, routing, solution, num_routes):
    """Get vehicle routes from a solution and store them in an array."""
    # Get vehicle routes and store them in a two dimensional array whose
    # i,j entry is the jth location visited by vehicle i along its route.
    routes = []
    for route_nbr in range(num_routes):
        index = routing.Start(route_nbr)
        route = [manager.IndexToNode(index)]
        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))
        routes.append(route)
    return routes

def print_solution(data, manager, routing, assignment):
    output = {
        "callback_url": data['adapter'].callback_url,
        "num_unserved": 0,
        "unserved": [],
        "solution": {},
        "polylines": {},
        "total_distance": 0,
        "total_travel_time": 0,
        "total_idle_time": 0, #TODO: Code later
    }
    plan = {}

    """Prints assignment on console."""
    # print('The Objective Value is {0}'.format(assignment.ObjectiveValue()))

    # Display dropped nodes.
    dropped_nodes = 'Dropped nodes:'
    for node in range(routing.Size()):
        if routing.IsStart(node) or routing.IsEnd(node):
            continue
        if assignment.Value(routing.NextVar(node)) == node:
            node_index = manager.IndexToNode(node)
            dropped_nodes += ' {}'.format(node_index)
            item = data['locations'][node_index]
            output['unserved'].append(item.location.id)
            output['num_unserved'] += 1
    print(dropped_nodes)

    # Display routes
    capacities = data['capacities']
    capacities_dimension = {}
    route_load_init = {}
    for capacity_key in capacities:
        capacity_dimension = routing.GetDimensionOrDie('Capacity' + capacity_key)
        capacities_dimension[capacity_key] = capacity_dimension
        route_load_init[capacity_key] = 0
    
    time_dimension = routing.GetDimensionOrDie('Time')
    
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        start_index = index

        route = []
        route_distance = 0
        distance_next = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
       
            # For route
            route_detail = {}
            route_detail['index'] = index

            # For capacities
            route_load = route_load_init.copy()
            for capacity_key, capacity_dimension in capacities_dimension.items():
                # load_var = capacity_dimension.CumulVar(node_index)
                # load_value = assignment.Value(load_var)
                load_value = data['demands'][capacity_key][index]
                route_load[capacity_key] = load_value
            route_detail['loads'] = route_load

            # For time windows
            time_var = time_dimension.CumulVar(index)
            time_max = int(assignment.Max(time_var)) + data['service_times'][index]
            route_detail['time'] = [int(assignment.Min(time_var)), time_max]

            # Set next index
            previous_index = index
            index = assignment.Value(routing.NextVar(index))

            # For distance
            route_detail['distance'] = distance_next
            if (index > data['num_visits']):
                distance_next = data['distance_matrix'][previous_index][start_index]
            else:
                distance_next = data['distance_matrix'][previous_index][index]

            # Set route detail
            route.append(route_detail)

        # Set next index
        node_index = manager.IndexToNode(index)

        # For route
        route_detail = {}
        route_detail['index'] = start_index

        # For capacities
        route_load = route_load_init.copy()
        for capacity_key, capacity_dimension in capacities_dimension.items():
            load_var = capacity_dimension.CumulVar(index)
            load_value = assignment.Value(load_var)
            route_load[capacity_key] = load_value
        route_detail['loads'] = route_load

        # For time windows
        time_var = time_dimension.CumulVar(index)
        route_detail['time'] = [int(assignment.Min(time_var)), int(assignment.Max(time_var))]

        # For distance
        route_detail['distance'] = distance_next

        # Set route detail
        route.append(route_detail)

        # Set vehicle detail
        plan[vehicle_id] = route

    for vehicle_id, route in plan.items():
        plan_output = '\nRoute for vehicle {}:\n'.format(vehicle_id)
        route_solution = []
        total_distance = 0
        total_time = 0
        for route_detail in route:
            node_index = route_detail['index']

            # For loads
            loads = route_detail['loads']
            load_output = ''
            for capacity_key, capacity_value in loads.items():
                load_output += '({0}: {1}) '.format(
                    capacity_key,
                    capacity_value
                )

            time = route_detail['time']
            arrival_time = str(datetime.timedelta(seconds=time[0]))
            finish_time = str(datetime.timedelta(seconds=time[1]))
            duration_time = time[1] - time[0]
            distance = route_detail['distance']
            total_distance += distance
            total_time = time[0]
            plan_output += '[{0}] Distance ({1} km) Time ({2}, {3}, {4}) Loads ({5})\n'.format(
                node_index,
                distance / 1000,
                arrival_time,
                finish_time,
                duration_time / 60,
                load_output
            )

            item = data['locations'][node_index]
            route_solution.append({
                "location_id": item.location.id,
                "location_name": item.location.name,
                "arrival_time": arrival_time,
                "finish_time": finish_time,
                "distance": round(distance),
                "duration": duration_time,
                "lat": item.location.lat,
                "lng": item.location.lng,
            })
        if (len(route_solution)):
            route_solution[len(route_solution) - 1]['location_id'] = 'driver_end'
            route_solution[len(route_solution) - 1]['location_name'] = 'driver_end'
        # print(plan_output)
        item = data['locations'][node_index]
        output['solution'][item.id] = route_solution
        total_time = total_time - item.start_time.seconds

        output['total_distance'] = round(total_distance)
        output['total_travel_time'] = total_time
        print('Total distance of route: {} km'.format(total_distance / 1000))
        print('Total time of route: {}'.format(str(datetime.timedelta(seconds=total_time))))
        print('Total loads of route: {}'.format(load_output))

    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    requests.post(output['callback_url'], json = { "output": output })

def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']), data['num_vehicles'], data['starts'], data['ends'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Register distance callback
    # def distance_callback(from_index, to_index):
    #     """Returns the distance between the two nodes."""
    #     # Convert from routing variable Index to distance matrix NodeIndex.
    #     from_node = manager.IndexToNode(from_index)
    #     to_node = manager.IndexToNode(to_index)
    #     return data['distance_matrix'][from_node][to_node]
    # distance_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Register time callback
    transit_callback_index = routing.RegisterTransitCallback(partial(create_time_evaluator(data), manager))

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    # add_distance_dimension(routing, distance_callback_index, data)

    # Add Time constraint.
    add_time_window_constraints(routing, manager, data, transit_callback_index)

    # Creates capacities constraints for each vehicle.
    add_capacities_constraints(routing, manager, data)
    allow_drop_visits(routing, manager, data)
    
    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if assignment:
        print_solution(data, manager, routing, assignment)  
    else:
        print('No solution found !')

if __name__ == '__main__':
    start_time = time.time()
    print("--- ROUTE-ENGINE: ---")
    main()
    end_time = int(time.time() - start_time)
    end_time = str(datetime.timedelta(seconds=end_time))
    print("--- END: %s ---" % (end_time))

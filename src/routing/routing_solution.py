from pprint import pprint
from src.helper.mapbox_api import mapbox_directions
from src.problem.problem_helper import seconds_to_hhmm
from src.problem.problem_location import ProblemLocation


def format_dropped_nodes(data, manager, routing, assignment):
    dropped_nodes = []
    for node in range(routing.Size()):
        if routing.IsStart(node) or routing.IsEnd(node):
            continue
        if assignment.Value(routing.NextVar(node)) == node:
            node_index = manager.IndexToNode(node)
            item = data['locations'][node_index]
            dropped_nodes.append(item.id)
    return dropped_nodes


def get_routes(solution, routing, manager):
    """Get vehicle routes from a solution and store them in an array."""
    # Get vehicle routes and store them in a two dimensional array whose
    # i,j entry is the jth location visited by vehicle i along its route.
    routes = []
    for route_nbr in range(routing.vehicles()):
        index = routing.Start(route_nbr)
        route = [manager.IndexToNode(index)]
        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            route_index = manager.IndexToNode(index)
            # if route_index == 0: continue  # Ignore depot
            route.append(route_index)
        routes.append(route)
    return routes


def reformat_routes(routes, locations: list[ProblemLocation]):
    visits = []
    for i, route in enumerate(routes):
        steps = []
        for index in route:
            location = locations[index]
            steps.append(location.id)
        visits.append(steps)
    return visits


def get_route_distances(routes, distance_matrix):
    distances = []
    for i, route in enumerate(routes):
        route_distances = [0]
        pre_index = route[0]
        for index in route[1:]:
            route_distances.append(distance_matrix[pre_index][index])
            pre_index = index
        distances.append(route_distances)
    return distances


def get_route_distances2(solution, routing):
    distances = []
    for route_nbr in range(routing.vehicles()):
        index = routing.Start(route_nbr)
        route_distances = [0]
        while not routing.IsEnd(index):
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            distance = routing.GetArcCostForVehicle(previous_index, index, route_nbr)
            route_distances.append(distance)
        distances.append(route_distances)
    return distances


def get_cumul_data(solution, routing, dimension):
    """Get cumulative data from a dimension and store it in an array."""
    cumul_data = []
    for route_nbr in range(routing.vehicles()):
        route_data = []
        index = routing.Start(route_nbr)
        dim_var = dimension.CumulVar(index)
        slack_var = dimension.SlackVar(index)
        route_data.append([
            solution.Min(dim_var), solution.Max(dim_var),
            # solution.Min(slack_var), solution.Max(slack_var)
        ])
        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            dim_var = dimension.CumulVar(index)
            slack_var = dimension.SlackVar(index)
            route_data.append([
                solution.Min(dim_var), solution.Max(dim_var),
                # solution.Min(slack_var), solution.Max(slack_var),
            ])
        cumul_data.append(route_data)
    return cumul_data


def get_route_times(time_steps, data, routes):
    time_windows = data['time_windows']
    distance_matrix = data['distance_matrix']
    service_times = data['service_times']
    vehicle_speed = data['vehicle_speed']
    times = []

    for i in range(len(time_steps)):
        time_window = time_steps[i]
        route_step = routes[i]

        route_time = []
        pre_time = time_window[0]
        pre_step_index = route_step[0]

        for index in range(0, len(time_window)):
            time = time_window[index]
            step_index = route_step[index]

            travel_time = int(distance_matrix[pre_step_index][step_index] / vehicle_speed)
            start_seconds = pre_time[1] + travel_time
            if start_seconds < time_windows[step_index][0]:
                start_seconds = time_windows[step_index][0]
            start = seconds_to_hhmm(start_seconds)

            service_time = service_times[step_index]
            end_seconds = start_seconds + service_time
            end = seconds_to_hhmm(end_seconds)

            route_time.append((start, end))
            pre_time = (start_seconds, end_seconds)
            pre_step_index = step_index
        times.append(route_time)
    return times


def get_travel_times(time_steps, data, routes):
    distance_matrix = data['distance_matrix']
    vehicle_speed = data['vehicle_speed']
    times = []

    def cal_travel_time(from_index, to_index):
        return int(distance_matrix[from_index][to_index] / vehicle_speed)

    for i in range(len(time_steps)):
        time_window = time_steps[i]
        route_step = routes[i]
        vehicle_index = route_step[0]

        route_time = []
        for index in range(len(time_window)):
            step_index = route_step[index]
            travel_time = cal_travel_time(vehicle_index, step_index)
            route_time.append(travel_time)

        times.append(route_time)
    return times


def get_service_times(data, routes):
    service_times = data['service_times']
    times = []

    for route in routes:
        route_time = [0]
        for index in route[1:]:
            service_time = service_times[index]
            route_time.append(service_time)

        times.append(route_time)
    return times


def get_route_polyline(routes, data):
    polyline = data['polyline']
    access_token = data['mapbox']
    locations = data['locations']
    geometry = []

    if not polyline:
        return geometry

    for route in routes:
        route_locations = []
        for index in route[1:]:
            route_locations.append(locations[index])

        polyline = mapbox_directions(route_locations, access_token)
        geometry.append(polyline)
    return geometry


def get_dimensions(data, routing):
    capacities = data['capacities']
    capacities_dimension = {}
    route_load_init = {}
    for capacity_key in capacities:
        capacity_dimension = routing.GetDimensionOrDie('Capacity' + capacity_key)
        capacities_dimension[capacity_key] = capacity_dimension
        route_load_init[capacity_key] = 0

    time_dimension = routing.GetDimensionOrDie('Time')
    return {'time': time_dimension, 'capacities': capacities_dimension, 'route_load_init': route_load_init}


# def format_routes(data, manager, routing, assignment):
#     dimensions = get_dimensions(data, routing)
#     capacities_dimension = dimensions.get('capacities')
#     route_load_init = dimensions.get('route_load_init')
#     time_dimension = dimensions.get('time')
#     plan = {}
#
#     for vehicle_id in range(data['num_vehicles']):
#         index = routing.Start(vehicle_id)
#         vehicle_index = index
#         plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
#
#         route = []
#         route_distance = 0
#         route_load = route_load_init.copy()
#         distance_next = 0
#         route_detail = {}
#         while not routing.IsEnd(index):
#             # For time windows
#             time_var = time_dimension.CumulVar(index)
#             plan_output += '{0} Time({1},{2}) -> '.format(manager.IndexToNode(index),
#                                                           assignment.Min(time_var), assignment.Max(time_var))
#
#             time_min = int(assignment.Min(time_var))
#             time_max = int(assignment.Max(time_var)) + data['service_times'][index]
#             route_detail['time'] = [time_min, time_max]
#
#             # For route
#             route_detail['index'] = index
#
#             # For capacities
#             for capacity_key, capacity_dimension in capacities_dimension.items():
#                 # load_var = capacity_dimension.CumulVar(node_index)
#                 # load_value = assignment.Value(load_var)
#                 load_value = data['demands'][capacity_key][index]
#                 route_load[capacity_key] = load_value
#             route_detail['loads'] = route_load
#
#             # Set next index
#             previous_index = index
#             index = assignment.Value(routing.NextVar(index))
#
#             # For distance
#             route_detail['distance'] = distance_next
#             if (index > data['num_visits']):
#                 distance_next = data['distance_matrix'][previous_index][vehicle_index]
#             else:
#                 distance_next = data['distance_matrix'][previous_index][index]
#
#             # Set route detail
#             route.append(route_detail)
#
#         # Set next index
#         node_index = manager.IndexToNode(index)
#
#         # For route
#         route_detail = {'index': vehicle_index}
#
#         # For capacities
#         route_load = route_load_init.copy()
#         for capacity_key, capacity_dimension in capacities_dimension.items():
#             load_var = capacity_dimension.CumulVar(index)
#             load_value = assignment.Value(load_var)
#             route_load[capacity_key] = load_value
#         route_detail['loads'] = route_load
#
#         # For time windows
#         time_var = time_dimension.CumulVar(index)
#         route_detail['time'] = [int(assignment.Min(time_var)), int(assignment.Max(time_var))]
#
#         # For distance
#         route_detail['distance'] = distance_next
#
#         # Set route detail
#         route.append(route_detail)
#
#         # Set vehicle detail
#         plan[vehicle_id] = route
#     return plan


def format_solution(data, manager, routing, assignment):
    """Prints assignment on console."""
    # print('Objective: {} meters'.format(assignment.ObjectiveValue()))

    # print('Breaks:')
    # intervals = assignment.IntervalVarContainer()
    # for i in xrange(intervals.Size()):
    #     brk = intervals.Element(i)
    #     if brk.PerformedValue() == 1:
    #         print('{}: Start({}) Duration({})'.format(
    #             brk.Var().Name(),
    #             brk.StartValue(),
    #             brk.DurationValue()))
    #     else:
    #         print('{}: Unperformed'.format(brk.Var().Name()))

    # Display dropped nodes.
    dropped_nodes = format_dropped_nodes(data, manager, routing, assignment)

    # Display routes
    routes = get_routes(assignment, routing, manager)

    # Reformat routes
    new_routes = reformat_routes(routes, data['locations'])

    # Display distances
    # distances = get_route_distances(routes, data['distance_matrix'])
    distances = get_route_distances2(assignment, routing)

    # Display times
    time_dimension = routing.GetDimensionOrDie('Time')
    data_times = get_cumul_data(assignment, routing, time_dimension)
    times = get_route_times(data_times, data, routes)

    # Display travel times
    travel_times = get_travel_times(data_times, data, routes)

    # Display service times
    service_times = get_service_times(data, routes)

    # Display polyline
    polyline = get_route_polyline(routes, data)

    # Display solution
    solution = {
        'objective': assignment.ObjectiveValue(),
        'dropped_nodes': dropped_nodes,
        'routes': routes, 'new_routes': new_routes, 'distances': distances,
        'time_windows': times, 'travel_times': travel_times, 'service_times': service_times,
        'polyline': polyline
    }
    pprint(solution)

    return solution

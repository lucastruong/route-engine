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


def get_routes(solution, routing, manager, virtual_depot_index: int):
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
            # Ignore virtual depot
            if route_index == virtual_depot_index:
                continue
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


def reformat_routes_with_root_id(routes, locations: list[ProblemLocation]):
    visits = []
    for i, route in enumerate(routes):
        steps = []
        for index in route:
            location = locations[index]
            steps.append(location.id_root)
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


def get_route_distances2(solution, routing, manager, virtual_depot_index: int):
    distances = []
    for route_nbr in range(routing.vehicles()):
        index = routing.Start(route_nbr)
        route_distances = [0]
        while not routing.IsEnd(index):
            previous_index = index
            index = solution.Value(routing.NextVar(index))

            # Ignore virtual depot
            route_index = manager.IndexToNode(index)
            if route_index == virtual_depot_index:
                continue

            distance = routing.GetArcCostForVehicle(previous_index, index, route_nbr)
            route_distances.append(distance)
        distances.append(route_distances)
    return distances


def get_cumul_data(solution, routing, manager, dimension, virtual_depot_index: int):
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

            # Ignore virtual depot
            route_index = manager.IndexToNode(index)
            if route_index == virtual_depot_index:
                continue

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
    routes = get_routes(assignment, routing, manager, data['virtual_depot_index'])

    # Reformat routes
    route_ids = reformat_routes(routes, data['locations'])

    # Reformat routes with root_id
    route_root_ids = reformat_routes_with_root_id(routes, data['locations'])

    # Display distances
    distances = get_route_distances(routes, data['distance_matrix'])
    # distances = get_route_distances2(assignment, routing, manager, data['virtual_depot_index'])

    # Display times
    time_dimension = routing.GetDimensionOrDie('Time')
    data_times = get_cumul_data(assignment, routing, manager, time_dimension, data['virtual_depot_index'])
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
        'routes': routes,
        'route_ids': route_ids, 'route_root_ids': route_root_ids,
        'distances': distances, 'time_windows': times,
        'travel_times': travel_times, 'service_times': service_times,
        'polyline': polyline
    }
    # pprint(solution)

    return solution



def routific_format_solution(solution: dict):
    dropped_nodes = solution.get('dropped_nodes')
    routes = solution.get('routes')
    route_root_ids = solution.get('route_root_ids')
    route_ids = solution.get('route_ids')
    time_windows = solution.get('time_windows')
    service_times = solution.get('service_times')
    travel_times = solution.get('travel_times')
    distances = solution.get('distances')
    polyline = solution.get('polyline')
    total_travel_time = 0

    solution = {}
    for route_index in range(len(routes)):
        route = routes[route_index]
        time_window = time_windows[route_index]
        distance = distances[route_index]
        service_time = service_times[route_index]
        travel_time = travel_times[route_index]
        route_root_id = route_root_ids[route_index]
        route_id = route_ids[route_index]

        vehicle_id = route_root_id[0]
        solution[vehicle_id] = []

        for step_index in range(len(route)):
            location_id = route_id[step_index]
            location_id_sub = '_start' if step_index == 0 and '_start' not in location_id else ''
            solution[vehicle_id].append({
                "location_id": location_id + location_id_sub,
                "arrival_time": time_window[step_index][0],
                "finish_time": time_window[step_index][1],
                "distance": distance[step_index],
                "duration": int(service_time[step_index] / 60),
                "minutes": int(travel_time[step_index] / 60)
            })
            total_travel_time += travel_time[step_index]

    polylines = {}
    for polyline_index in range(len(polyline)):
        polyline_route = polyline[polyline_index]
        route_root_id = route_root_ids[polyline_index]
        vehicle_id = route_root_id[0]
        polylines[vehicle_id] = [polyline_route]

    out = {
        'status': 'success',
        'total_travel_time': total_travel_time,
        'total_idle_time': 0,
        'num_unserved': len(dropped_nodes),
        'unserved': dropped_nodes,
        'solution': solution,
        'polylines': polylines
    }

    return out

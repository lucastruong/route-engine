

def routific_format_solution(solution: dict):
    dropped_nodes = solution.get('dropped_nodes')
    routes = solution.get('routes')
    route_root_ids = solution.get('route_root_ids')
    route_ids = solution.get('route_ids')
    time_windows = solution.get('time_windows')
    service_times = solution.get('service_times')
    travel_times = solution.get('travel_times')
    waiting_times = solution.get('waiting_times')
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
        waiting_time = waiting_times[route_index]
        route_root_id = route_root_ids[route_index]
        route_id = route_ids[route_index]

        vehicle_id = route_root_id[0]
        solution[vehicle_id] = []
        route_len = len(route)

        # Check route is empty solution
        location_id_last = route_id[-1]
        if route_len <= 2 and vehicle_id in location_id_last:
            continue

        for step_index in range(route_len):
            location_id = route_id[step_index]
            location_id_sub = '_start' if step_index == 0 and '_start' not in location_id else ''
            solution[vehicle_id].append({
                "location_id": location_id + location_id_sub,
                "arrival_time": time_window[step_index][0],
                "finish_time": time_window[step_index][1],
                "distance": distance[step_index],
                "duration": int(service_time[step_index] / 60),
                "travel_mins": int(travel_time[step_index] / 60),
                "waiting_mins": int(waiting_time[step_index] / 60),
                # "type": "",
            })
            total_travel_time += travel_time[step_index]

    polylines = {}
    for polyline_index in range(len(polyline)):
        polyline_route = polyline[polyline_index]
        route_root_id = route_root_ids[polyline_index]
        route_id = route_ids[polyline_index]
        route = routes[polyline_index]

        vehicle_id = route_root_id[0]
        route_len = len(route)

        # Check route is empty solution
        location_id_last = route_id[-1]
        if route_len <= 2 and vehicle_id in location_id_last:
            continue

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


def routific_callback_solution(job_id: str, out, solution: dict):
    output = {
        'id': job_id,
        'output': out,
        'fleet': len(solution.get('vehicles')),
        'visits': len(solution.get('visits')),
    }

    return output

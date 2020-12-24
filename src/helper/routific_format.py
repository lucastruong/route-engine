import numpy as np


def routific_format_solution(solution: dict):
    dropped_nodes = solution.get('dropped_nodes')
    routes = solution.get('routes')
    new_routes = solution.get('new_routes')
    time_windows = solution.get('time_windows')
    service_times = solution.get('service_times')
    travel_times = solution.get('travel_times')
    distances = solution.get('distances')

    solution = {}
    for route_index in range(len(routes)):
        route = routes[route_index]
        time_window = time_windows[route_index]
        distance = distances[route_index]
        service_time = service_times[route_index]
        travel_time = travel_times[route_index]
        new_route = new_routes[route_index]

        vehicle_id = new_route[0]
        solution[vehicle_id] = []

        for step_index in range(len(route)):
            solution[vehicle_id].append({
                "location_id": new_route[step_index],
                "arrival_time": time_window[step_index][0],
                "finish_time": time_window[step_index][1],
                "distance": distance[step_index],
                "duration": int(service_time[step_index] / 60),
                "minutes": int(travel_time[step_index] / 60)
            })

    out = {
        'status': 'success',
        'total_travel_time': np.sum(np.array(travel_times)),
        'total_idle_time': 0,
        'num_unserved': len(dropped_nodes),
        'unserved': dropped_nodes,
        'solution': solution
    }

    return out

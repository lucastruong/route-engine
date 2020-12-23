import numpy as np


def routific_format_solution(solution: dict):
    dropped_nodes = solution.get('dropped_nodes')
    travel_times = np.array(solution.get('travel_times'))

    out = {
        'status': 'success',
        'total_travel_time': np.sum(travel_times),
        'total_idle_time': 0,
        'num_unserved': len(dropped_nodes),
        'unserved': dropped_nodes,
    }

    return out

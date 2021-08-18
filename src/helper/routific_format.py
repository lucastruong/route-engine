from typing import List

from src.problem.problem_helper import seconds_to_hhmm
from src.problem.problem_location import ProblemLocation


def routific_format_solution(solution: dict):
    problem_solution = solution.get('solution')
    dropped_nodes = solution.get('dropped_nodes')
    total_travel_time = 0

    solution = {}
    polylines = {}

    for vehicle_id, vehicle_route in problem_solution.routes.items():
        locations: List[ProblemLocation] = vehicle_route.get('steps')
        geometry = vehicle_route.get('geometry')
        solution[vehicle_id] = []

        # For polyline
        if geometry is not None:
            polylines[vehicle_id] = [geometry]

        # For steps
        for idx, location in enumerate(locations):
            solution[vehicle_id].append({
                'location_id': location.id,
                'arrival_time': seconds_to_hhmm(location.arrival_time),
                'finish_time': seconds_to_hhmm(location.finish_time),
                'distance': location.distance,
                'duration': int(location.service_time / 60),
                'travel_mins': int(location.travel_time / 60),
                'waiting_mins': int(location.waiting_time/ 60),
                'type': location.type,
            })
            total_travel_time += location.travel_time

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

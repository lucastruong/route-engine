import json
import os
import unittest

from src.routing.routing_problem import optimize_problem
from src.helper.routific_format import routific_format_solution


def read_problem_json(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    f = open(dir_path + "/data/" + file_name, "r")
    json_obj = json.loads(f.read())
    f.close()
    return json_obj


class PdpTest(unittest.TestCase):
    def testBasic(self):
        problem_json = read_problem_json('pdp_basic.json')
        solution = optimize_problem(problem_json)

        expected_objective = 12613
        expected_routes = [[1, 2, 4, 5, 3]]
        expected_route_ids = [['vehicle_1',
                               'order_1_pickup',
                               'order_2_pickup',
                               'order_2_delivery',
                               'order_1_delivery']]
        expected_distances = [[0, 6965, 630, 834, 4184]]
        expected_travel_times = [[0, 783, 847, 901, 1306]]
        expected_service_times = [[0, 300, 900, 1200, 600]]

        self.assertEqual(expected_objective, solution.get('objective'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))
        self.assertEqual(expected_distances, solution.get('distances'))
        self.assertEqual(expected_travel_times, solution.get('travel_times'))
        self.assertEqual(expected_service_times, solution.get('service_times'))

    def testRoutificFormat(self):
        problem_json = read_problem_json('pdp_routific_format.json')
        solution = optimize_problem(problem_json)
        out = routific_format_solution(solution)

        expected_out = {
            'status': 'success',
            'total_travel_time': 1416,
            'total_idle_time': 0,
            'num_unserved': 0,
            'unserved': [],
            'solution': {
                'vehicle_1': [{'arrival_time': '08:00',
                               'distance': 0,
                               'duration': 0,
                               'finish_time': '08:00',
                               'location_id': 'vehicle_1_start',
                               'minutes': 0},
                              {'arrival_time': '08:13',
                               'distance': 6965,
                               'duration': 10,
                               'finish_time': '08:23',
                               'location_id': 'order_1_pickup',
                               'minutes': 13},
                              {'arrival_time': '08:24',
                               'distance': 630,
                               'duration': 0,
                               'finish_time': '08:24',
                               'location_id': 'order_2_pickup',
                               'minutes': 1},
                              {'arrival_time': '08:25',
                               'distance': 834,
                               'duration': 0,
                               'finish_time': '08:25',
                               'location_id': 'order_2_delivery',
                               'minutes': 1},
                              {'arrival_time': '09:00',
                               'distance': 4184,
                               'duration': 5,
                               'finish_time': '09:05',
                               'location_id': 'order_1_delivery',
                               'minutes': 7}],
                'vehicle_2': [],
            },
            'polylines': {'vehicle_1': ['q`baA_mujSnA`AgDnDnL`O`@nL~OwAaGfRuDz_@rZtLnjA|MhQ|GhRlTfF~RhRpcBnJjaAoCMw'
                                        '@aLQi@pFyBvN`KgBnDrB|Cd@m@e@l@tAzBiFbFsEqF_Bh@`KnJf]fAjGnIp@i@sC}F`FaCy'
                                        '@uAqBrApBsAx@tAaF`CkEmBsNFjMXhHnGwMfRoCfMqB|KuKaB|ZfY}Cr@sBvIcEzj@xBPrGjv'
                                        '@}Yha@yHjE}Bjo@']},
        }

        self.assertEqual(expected_out, out)


if __name__ == '__main__':
    unittest.main()

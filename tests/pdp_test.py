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

        expected_routes = [[1, 2, 4, 5, 3]]
        expected_route_ids = [['vehicle_1',
                               'order_1_PICKUP',
                               'order_2_PICKUP',
                               'order_2_DELIVERY',
                               'order_1_DELIVERY']]
        expected_distances = [[0, 6965, 630, 834, 4184]]
        expected_travel_times = [[0, 835, 75, 100, 502]]
        expected_service_times = [[0, 300, 900, 1200, 600]]

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
            'total_travel_time': 1512,
            'total_idle_time': 0,
            'num_unserved': 0,
            'unserved': [],
            'solution': {'vehicle_1': [{'arrival_time': '08:00',
                                        'distance': 0,
                                        'duration': 0,
                                        'finish_time': '08:00',
                                        'location_id': 'vehicle_1_start',
                                        'travel_mins': 0,
                                        'type': 'VEHICLE',
                                        'waiting_mins': 0},
                                       {'arrival_time': '08:13',
                                        'distance': 6965,
                                        'duration': 10,
                                        'finish_time': '08:23',
                                        'location_id': 'order_1_PICKUP',
                                        'travel_mins': 13,
                                        'type': 'PICKUP',
                                        'waiting_mins': 0},
                                       {'arrival_time': '08:25',
                                        'distance': 630,
                                        'duration': 0,
                                        'finish_time': '08:25',
                                        'location_id': 'order_2_PICKUP',
                                        'travel_mins': 1,
                                        'type': 'PICKUP',
                                        'waiting_mins': 0},
                                       {'arrival_time': '08:26',
                                        'distance': 834,
                                        'duration': 0,
                                        'finish_time': '08:26',
                                        'location_id': 'order_2_DELIVERY',
                                        'travel_mins': 1,
                                        'type': 'DELIVERY',
                                        'waiting_mins': 0},
                                       {'arrival_time': '09:00',
                                        'distance': 4184,
                                        'duration': 5,
                                        'finish_time': '09:05',
                                        'location_id': 'order_1_DELIVERY',
                                        'travel_mins': 8,
                                        'type': 'DELIVERY',
                                        'waiting_mins': 24}],
                         'vehicle_2': []},
            'polylines': {},
        }

        self.assertEqual(expected_out, out)

    # def testLargeProblem(self):
    #     problem_json = read_problem_json('pdp_large.json')
    #     solution = optimize_problem(problem_json)
    #     out = routific_format_solution(solution)
    #
    #     expected_out = {
    #         'status': 'success',
    #         'total_travel_time': 1416,
    #         'total_idle_time': 0,
    #         'num_unserved': 0,
    #         'unserved': [],
    #         'solution': {'vehicle_1': [{'arrival_time': '08:00',
    #                                     'distance': 0,
    #                                     'duration': 0,
    #                                     'finish_time': '08:00',
    #                                     'location_id': 'vehicle_1_start',
    #                                     'travel_mins': 0,
    #                                     'type': 'VEHICLE',
    #                                     'waiting_mins': 0},
    #                                    {'arrival_time': '08:13',
    #                                     'distance': 6965,
    #                                     'duration': 10,
    #                                     'finish_time': '08:23',
    #                                     'location_id': 'order_1_PICKUP',
    #                                     'travel_mins': 13,
    #                                     'type': 'PICKUP',
    #                                     'waiting_mins': 0},
    #                                    {'arrival_time': '08:24',
    #                                     'distance': 630,
    #                                     'duration': 0,
    #                                     'finish_time': '08:24',
    #                                     'location_id': 'order_2_PICKUP',
    #                                     'travel_mins': 1,
    #                                     'type': 'PICKUP',
    #                                     'waiting_mins': 0},
    #                                    {'arrival_time': '08:25',
    #                                     'distance': 834,
    #                                     'duration': 0,
    #                                     'finish_time': '08:25',
    #                                     'location_id': 'order_2_DELIVERY',
    #                                     'travel_mins': 1,
    #                                     'type': 'DELIVERY',
    #                                     'waiting_mins': 0},
    #                                    {'arrival_time': '09:00',
    #                                     'distance': 4184,
    #                                     'duration': 5,
    #                                     'finish_time': '09:05',
    #                                     'location_id': 'order_1_DELIVERY',
    #                                     'travel_mins': 7,
    #                                     'type': 'DELIVERY',
    #                                     'waiting_mins': 26}],
    #                      'vehicle_2': []},
    #         'polylines': {},
    #     }
    #
    #     self.assertEqual(expected_out, out)


if __name__ == '__main__':
    unittest.main()

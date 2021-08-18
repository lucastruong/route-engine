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


class VrpTest(unittest.TestCase):
    def testTSP(self):
        problem_json = read_problem_json('vrp_tsp.json')
        solution = optimize_problem(problem_json)

        expected_objective = 12214
        expected_routes = [[1, 2, 3]]
        expected_route_ids = [['vehicle_1', 'location_1', 'location_2']]
        expected_distances = [[0, 6965, 5249]]
        expected_travel_times = [[0, 783, 590]]
        expected_service_times = [[0, 300, 600]]

        self.assertEqual(expected_objective, solution.get('objective'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))
        self.assertEqual(expected_distances, solution.get('distances'))
        self.assertEqual(expected_travel_times, solution.get('travel_times'))
        self.assertEqual(expected_service_times, solution.get('service_times'))

    def testVehicleEndLocation(self):
        problem_json = read_problem_json('vrp_vehicle_end_location.json')
        solution = optimize_problem(problem_json)

        expected_routes = [[1, 3, 4, 2]]
        expected_route_ids = [['vehicle_1', 'location_1', 'location_2', 'vehicle_01_end']]
        expected_distances = [[0, 6965, 5249, 2854]]

        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))
        self.assertEqual(expected_distances, solution.get('distances'))

    def testLocationIds(self):
        problem_json = read_problem_json('vrp_location_ids.json')
        solution = optimize_problem(problem_json)

        expected_route_ids = [['vehicle_1', 'location_01_start', 'location_2', 'vehicle_01_end']]
        self.assertEqual(expected_route_ids, solution.get('route_ids'))

    def testVehicleCapacity(self):
        problem_json = read_problem_json('vrp_capacity.json')
        solution = optimize_problem(problem_json)

        expected_dropped_nodes = ['location_2']
        expected_routes = [[1, 2]]
        expected_route_ids = [['vehicle_1', 'location_1']]

        self.assertEqual(expected_dropped_nodes, solution.get('dropped_nodes'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))

    def testVehicleCapacityIsString(self):
        problem_json = read_problem_json('vrp_capacity_is_string.json')
        solution = optimize_problem(problem_json)

        expected_dropped_nodes = ['location_2']
        expected_routes = [[1, 2]]
        expected_route_ids = [['vehicle_1', 'location_1']]

        self.assertEqual(expected_dropped_nodes, solution.get('dropped_nodes'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))

    def testVehicleSkill(self):
        problem_json = read_problem_json('vrp_skill.json')
        solution = optimize_problem(problem_json)

        expected_dropped_nodes = ['location_3']
        expected_routes = [[1, 2, 3]]
        expected_route_ids = [['vehicle_1', 'location_1', 'location_2']]

        self.assertEqual(expected_dropped_nodes, solution.get('dropped_nodes'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))

    def testTimeWindows(self):
        problem_json = read_problem_json('vrp_time_windows.json')
        solution = optimize_problem(problem_json)
        expected_time_windows = [[('08:00', '08:00'), ('08:13', '08:23'), ('09:00', '09:05')]]
        expected_travel_times = [[0, 783, 590]]
        expected_service_times = [[0, 600, 300]]
        expected_waiting_times = [[0, 0, 1627]]

        self.assertEqual(expected_time_windows, solution.get('time_windows'))
        self.assertEqual(expected_travel_times, solution.get('travel_times'))
        self.assertEqual(expected_service_times, solution.get('service_times'))
        self.assertEqual(expected_waiting_times, solution.get('waiting_times'))

    def testBalance(self):
        problem_json = read_problem_json('vrp_balance.json')
        solution = optimize_problem(problem_json)

        expected_routes = [
            [1, 3],
            [2, 4],
        ]
        expected_route_ids = [
            ['vehicle_1', 'location_1'],
            ['vehicle_2', 'location_2'],
        ]

        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))

    def testOrder(self):
        problem_json = read_problem_json('vrp_order.json')
        solution = optimize_problem(problem_json)

        expected_routes = [[1, 3, 4, 2]]
        expected_route_ids = [['vehicle_1', 'location_2', 'location_3', 'location_1']]

        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))

    def testPolylineByMapbox(self):
        problem_json = read_problem_json('vrp_polyline.json')
        solution = optimize_problem(problem_json)

        expected_polyline = ['q`baA_mujSnA`AgDnDnL`O|BfVaQhJjSvV}@pCrZtLnjA|MhQ|GhRlTfF~RhRpcBnJjaAoCMw@aLQi@pFyBvN'
                             '`KgBnDrB|Cd@m@e@l@tAzBiFbFkGoHIeCaAoQwDSuAnC^~InA`EwKr]}CzNz@~YfJpRth@pg@`EdEsD`EW`IvG'
                             '~r@}Yha@yHjE}Bjo@']
        expected_time_windows = [[('08:00', '08:00'), ('08:17', '08:27'), ('09:00', '09:05')]]
        expected_distances = [[0, 9313, 7496]]
        expected_travel_times = [[0, 1047, 843]]
        expected_service_times = [[0, 600, 300]]
        expected_waiting_times = [[0, 0, 1110]]

        self.assertEqual(expected_polyline, solution.get('polyline'))
        self.assertEqual(expected_time_windows, solution.get('time_windows'))
        self.assertEqual(expected_distances, solution.get('distances'))
        self.assertEqual(expected_travel_times, solution.get('travel_times'))
        self.assertEqual(expected_service_times, solution.get('service_times'))
        self.assertEqual(expected_waiting_times, solution.get('waiting_times'))

    def testRoutificFormat(self):
        problem_json = read_problem_json('vrp_routific_format.json')
        solution = optimize_problem(problem_json)
        out = routific_format_solution(solution)

        expected_out = {
            'status': 'success',
            'total_travel_time': 1890,
            'total_idle_time': 0,
            'num_unserved': 0,
            'unserved': [],
            'solution': {
                'vehicle_1': [{'arrival_time': '08:00',
                               'distance': 0,
                               'duration': 0,
                               'finish_time': '08:00',
                               'location_id': 'vehicle_1_start',
                               'travel_mins': 0,
                               'waiting_mins': 0,
                               'type': 'VEHICLE',
                               },
                              {'arrival_time': '08:17',
                               'distance': 9313,
                               'duration': 10,
                               'finish_time': '08:27',
                               'location_id': 'location_1_id',
                               'travel_mins': 17,
                               'waiting_mins': 0,
                               'type': 'PICKUP',
                               },
                              {'arrival_time': '09:00',
                               'distance': 7496,
                               'duration': 5,
                               'finish_time': '09:05',
                               'location_id': 'location_2_id',
                               'travel_mins': 14,
                               'waiting_mins': 18,
                               'type': 'PICKUP',
                               }
                              ],
                'vehicle_2': [],
            },
            'polylines': {'vehicle_1': ['q`baA_mujSnA`AgDnDnL`O|BfVaQhJjSvV}@pCrZtLnjA|MhQ|GhRlTfF~RhRpcBnJjaAoCMw'
                                        '@aLQi@pFyBvN`KgBnDrB|Cd@m@e@l@tAzBiFbFkGoHIeCaAoQwDSuAnC^~InA`EwKr]}CzNz'
                                        '@~YfJpRth@pg@`EdEsD`EW`IvG~r@}Yha@yHjE}Bjo@']},
        }

        self.assertEqual(expected_out, out)


if __name__ == '__main__':
    unittest.main()

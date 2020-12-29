import json
import os
import unittest

from problem import main
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
        solution = main(problem_json)

        expected_objective = 23830
        expected_routes = [[0, 1, 2, 0]]
        expected_route_ids = [['vehicle_1', 'location_1', 'location_2', 'vehicle_1']]
        expected_distances = [[0, 6965, 5249, 11616]]
        expected_travel_times = [[0, 783, 1306, 0]]
        expected_service_times = [[0, 300, 600, 0]]

        self.assertEqual(expected_objective, solution.get('objective'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))
        self.assertEqual(expected_distances, solution.get('distances'))
        self.assertEqual(expected_travel_times, solution.get('travel_times'))
        self.assertEqual(expected_service_times, solution.get('service_times'))

    def testVehicleEndLocation(self):
        problem_json = read_problem_json('vrp_vehicle_end_location.json')
        solution = main(problem_json)

        expected_objective = 15221
        expected_routes = [[0, 1, 2, 3]]
        expected_route_ids = [['vehicle_1', 'location_1', 'location_2', 'vehicle_1_end']]
        expected_distances = [[0, 6965, 5249, 3007]]

        self.assertEqual(expected_objective, solution.get('objective'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))
        self.assertEqual(expected_distances, solution.get('distances'))

    def testVehicleCapacity(self):
        problem_json = read_problem_json('vrp_capacity.json')
        solution = main(problem_json)

        expected_dropped_nodes = ['location_2']
        expected_routes = [[0, 1, 0]]
        expected_route_ids = [['vehicle_1', 'location_1', 'vehicle_1']]

        self.assertEqual(expected_dropped_nodes, solution.get('dropped_nodes'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))

    def testVehicleCapacityIsString(self):
        problem_json = read_problem_json('vrp_capacity_is_string.json')
        solution = main(problem_json)

        expected_dropped_nodes = ['location_2']
        expected_routes = [[0, 1, 0]]
        expected_route_ids = [['vehicle_1', 'location_1', 'vehicle_1']]

        self.assertEqual(expected_dropped_nodes, solution.get('dropped_nodes'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))

    def testVehicleSkill(self):
        problem_json = read_problem_json('vrp_skill.json')
        solution = main(problem_json)

        expected_dropped_nodes = ['location_3']
        expected_routes = [[0, 1, 2, 0]]
        expected_route_ids = [['vehicle_1', 'location_1', 'location_2', 'vehicle_1']]

        self.assertEqual(expected_dropped_nodes, solution.get('dropped_nodes'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))

    def testTimeWindows(self):
        problem_json = read_problem_json('vrp_time_windows.json')
        solution = main(problem_json)

        expected_time_windows = [[('08:00', '08:00'), ('08:13', '08:23'), ('09:00', '09:05'), ('09:26', '09:26')]]
        expected_travel_times = [[0, 783, 1306, 0]]

        self.assertEqual(expected_time_windows, solution.get('time_windows'))
        self.assertEqual(expected_travel_times, solution.get('travel_times'))

    def testBalance(self):
        problem_json = read_problem_json('vrp_balance.json')
        solution = main(problem_json)

        expected_routes = [
            [0, 2, 0],
            [1, 3, 1],
        ]
        expected_route_ids = [
            ['vehicle_1', 'location_1', 'vehicle_1'],
            ['vehicle_2', 'location_2', 'vehicle_2'],
        ]

        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))

    def testOrder(self):
        problem_json = read_problem_json('vrp_order.json')
        solution = main(problem_json)

        expected_routes = [[0, 2, 3, 1, 0]]
        expected_route_ids = [['vehicle_1', 'location_2', 'location_3', 'location_1', 'vehicle_1']]

        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_route_ids, solution.get('route_ids'))

    def testPolyline(self):
        problem_json = read_problem_json('vrp_polyline.json')
        solution = main(problem_json)

        expected_polyline = ['an{`A}|jjS|AbCyFnEoHuIJeR_FmAkAdFXlGnA`EwKr]}CzNz@~YfJpRth@pg@~L`LyGlHrf@rf@v@zBgk@ho@w'
                             '^vt@iBKNiC|Bko@xHkE|w@_gAib@oa@ek@ij@_JeRq@i['
                             'pPad@z@gAn@oBPeBmJkdAiNsxAeL_a@sPuQaIkDos@gKgEi@gg@mJaIiEOmUpIy\\_PvAa@oLoLaOnAmA_CoC'
                             '~B[']

        self.assertEqual(expected_polyline, solution.get('polyline'))

    def testRoutificFormat(self):
        problem_json = read_problem_json('vrp_routific_format.json')
        solution = main(problem_json)
        out = routific_format_solution(solution)

        expected_out = {
            'status': 'success',
            'total_travel_time': 2089,
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
                               'location_id': 'location_1_id',
                               'minutes': 13},
                              {'arrival_time': '09:00',
                               'distance': 5249,
                               'duration': 5,
                               'finish_time': '09:05',
                               'location_id': 'location_2_id',
                               'minutes': 21},
                              {'arrival_time': '09:26',
                               'distance': 11616,
                               'duration': 0,
                               'finish_time': '09:26',
                               'location_id': 'vehicle_1_start',
                               'minutes': 0}],
            },
            'polylines': {'vehicle_1': ['an{`A}|jjS|AbCyFnEoHuIJeR_FmAkAdFXlGnA`EwKr]}CzNz@~YfJpRth@pg@~L`LyGlHrf@rf@v@zBgk@ho@w^vt@iBKNiC|Bko@xHkE|w@_gAib@oa@ek@ij@_JeRq@i[pPad@z@gAn@oBPeBmJkdAiNsxAeL_a@sPuQaIkDos@gKgEi@gg@mJaIiEOmUpIy\\_PvAa@oLoLaOnAmA_CoC~B[']},
        }

        self.assertEqual(expected_out, out)


    def testComplexData(self):
        problem_json = read_problem_json('vrp_complex_data.json')
        solution = main(problem_json)
        out = routific_format_solution(solution)
        print(out)
        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()

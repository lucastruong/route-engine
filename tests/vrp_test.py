import json
import os
import unittest

from problem import main


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
        expected_new_routes = [['vehicle_1', 'location_1', 'location_2', 'vehicle_1']]
        expected_distances = [[0, 6965, 5249, 11616]]

        self.assertEqual(expected_objective, solution.get('objective'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_new_routes, solution.get('new_routes'))
        self.assertEqual(expected_distances, solution.get('distances'))

    def testVehicleEndLocation(self):
        problem_json = read_problem_json('vrp_vehicle_end_location.json')
        solution = main(problem_json)

        expected_objective = 15221
        expected_routes = [[0, 1, 2, 3]]
        expected_new_routes = [['vehicle_1', 'location_1', 'location_2', 'vehicle_1_end']]
        expected_distances = [[0, 6965, 5249, 3007]]

        self.assertEqual(expected_objective, solution.get('objective'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_new_routes, solution.get('new_routes'))
        self.assertEqual(expected_distances, solution.get('distances'))

    def testVehicleCapacity(self):
        problem_json = read_problem_json('vrp_capacity.json')
        solution = main(problem_json)

        expected_dropped_nodes = ['location_2']
        expected_routes = [[0, 1, 0]]
        expected_new_routes = [['vehicle_1', 'location_1', 'vehicle_1']]

        self.assertEqual(expected_dropped_nodes, solution.get('dropped_nodes'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_new_routes, solution.get('new_routes'))

    def testVehicleCapacityIsString(self):
        problem_json = read_problem_json('vrp_capacity_is_string.json')
        solution = main(problem_json)

        expected_dropped_nodes = ['location_2']
        expected_routes = [[0, 1, 0]]
        expected_new_routes = [['vehicle_1', 'location_1', 'vehicle_1']]

        self.assertEqual(expected_dropped_nodes, solution.get('dropped_nodes'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_new_routes, solution.get('new_routes'))

    def testVehicleSkill(self):
        problem_json = read_problem_json('vrp_skill.json')
        solution = main(problem_json)

        expected_dropped_nodes = ['location_3']
        expected_routes = [[0, 1, 2, 0]]
        expected_new_routes = [['vehicle_1', 'location_1', 'location_2', 'vehicle_1']]

        self.assertEqual(expected_dropped_nodes, solution.get('dropped_nodes'))
        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_new_routes, solution.get('new_routes'))

    def testTimeWindows(self):
        problem_json = read_problem_json('vrp_time_windows.json')
        solution = main(problem_json)

        expected_times = [
            [('08:00', '08:00'), ('08:13', '08:23'), ('09:00', '09:10'), ('09:21', '09:21')]
        ]

        self.assertEqual(expected_times, solution.get('times'))

if __name__ == '__main__':
    unittest.main()

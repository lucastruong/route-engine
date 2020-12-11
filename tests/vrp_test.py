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

        expected_routes = [[0, 1, 2, 0]]
        expected_new_routes = [['vehicle_1', 'location_1', 'location_2', 'vehicle_1']]
        expected_distances = [[0, 6965, 5249, 11616]]

        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_new_routes, solution.get('new_routes'))
        self.assertEqual(expected_distances, solution.get('distances'))

    def testVehicleEndLocation(self):
        problem_json = read_problem_json('vrp_tsp_end_location.json')
        solution = main(problem_json)

        expected_routes = [[0, 2, 3, 1]]
        expected_new_routes = [['vehicle_1', 'location_1', 'location_2', 'vehicle_1_end']]
        expected_distances = [[0, 6965, 5249, 3007]]

        self.assertEqual(expected_routes, solution.get('routes'))
        self.assertEqual(expected_new_routes, solution.get('new_routes'))
        self.assertEqual(expected_distances, solution.get('distances'))


if __name__ == '__main__':
    unittest.main()

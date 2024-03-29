# Copyright 2010-2018 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""pywrapcp unittest file."""

from __future__ import print_function

from functools import partial

import unittest

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

total = 0

def Distance(node_i, node_j):
    return node_i + node_j


def TransitDistance(manager, i, j):
    global total
    distance = Distance(manager.IndexToNode(i), manager.IndexToNode(j))
    total = total + distance
    # print("--- Distance: %s ---" % distance)
    # print("--- Total: %s ---" % total)
    return Distance(manager.IndexToNode(i), manager.IndexToNode(j))


def One(unused_i, unused_j):
    return 1


def Two(unused_i, unused_j):
    return 1


def Three(unused_i, unused_j):
    return 1


class Callback(object):

    def __init__(self, model):
        self.model = model
        self.costs = []

    def __call__(self):
        self.costs.append(self.model.CostVar().Max())


class PyWrapRoutingTest(unittest.TestCase):

    def testTSP(self):
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(4, 1, 0)
        model = pywrapcp.RoutingModel(manager)
        # Add cost function
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        self.assertEqual(pywrapcp.RoutingModel.ROUTING_NOT_SOLVED,
                         model.status())
        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE)
        assignment = model.SolveWithParameters(search_parameters)
        self.assertEqual(pywrapcp.RoutingModel.ROUTING_SUCCESS, model.status())
        self.assertEqual(12, assignment.ObjectiveValue())
        # Inspect solution
        index = model.Start(0)
        visited_nodes = []
        expected_visited_nodes = [1, 2, 3, 0]
        while not model.IsEnd(index):
            index = assignment.Value(model.NextVar(index))
            visited_nodes.append(manager.IndexToNode(index))
        self.assertEqual(expected_visited_nodes, visited_nodes)

    def testMultiDepot(self):
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(10, 2, [0, 1], [1, 0])
        model = pywrapcp.RoutingModel(manager)
        # Add cost function
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE)
        assignment = model.SolveWithParameters(search_parameters)
        self.assertEqual(89, assignment.ObjectiveValue())
        # Inspect solution
        index = model.Start(1)
        visited_nodes = []
        expected_visited_nodes = [2, 4, 6, 8, 3, 5, 7, 9, 0]
        while not model.IsEnd(index):
            index = assignment.Value(model.NextVar(index))
            visited_nodes.append(manager.IndexToNode(index))
        self.assertEqual(expected_visited_nodes, visited_nodes)
        self.assertTrue(
            model.IsEnd(assignment.Value(model.NextVar(model.Start(0)))))

    def testDimensionTSP(self):
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(10, 1, 0)
        model = pywrapcp.RoutingModel(manager)
        # Add cost function
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        # Add generic dimension
        model.AddDimension(cost, 90, 90, True, 'distance')
        distance_dimension = model.GetDimensionOrDie('distance')
        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE)
        assignment = model.SolveWithParameters(search_parameters)
        self.assertEqual(90, assignment.ObjectiveValue())
        # Inspect solution
        node = model.Start(0)
        cumul = 0
        while not model.IsEnd(node):
            self.assertEqual(cumul,
                             assignment.Value(
                                 distance_dimension.CumulVar(node)))
            next_node = assignment.Value(model.NextVar(node))
            cumul += Distance(node, next_node)
            node = next_node

    def testDimensionWithVehicleCapacitiesTSP(self):
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(10, 1, 0)
        model = pywrapcp.RoutingModel(manager)
        # Add cost function
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        # Add generic dimension
        model.AddDimensionWithVehicleCapacity(cost, 90, [90], True, 'distance')
        distance_dimension = model.GetDimensionOrDie('distance')
        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE)
        assignment = model.SolveWithParameters(search_parameters)
        self.assertEqual(90, assignment.ObjectiveValue())
        # Inspect solution
        node = model.Start(0)
        cumul = 0
        while not model.IsEnd(node):
            self.assertEqual(cumul,
                             assignment.Value(
                                 distance_dimension.CumulVar(node)))
            next_node = assignment.Value(model.NextVar(node))
            cumul += Distance(node, next_node)
            node = next_node

    def testDimensionWithVehicleTransitsTSP(self):
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(5, 1, 0)
        model = pywrapcp.RoutingModel(manager)
        # Add cost function
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        # Add generic dimension
        model.AddDimensionWithVehicleTransits([cost], 0, 20, True, 'distance')
        distance_dimension = model.GetDimensionOrDie('distance')
        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE)
        assignment = model.SolveWithParameters(search_parameters)
        self.assertEqual(20, assignment.ObjectiveValue())
        # Inspect solution
        node = model.Start(0)
        cumul = 0
        while not model.IsEnd(node):
            self.assertEqual(cumul,
                             assignment.Value(
                                 distance_dimension.CumulVar(node)))
            next_node = assignment.Value(model.NextVar(node))
            cumul += Distance(node, next_node)
            node = next_node

    def testDimensionWithVehicleTransitsVRP(self):
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(10, 3, 0)
        model = pywrapcp.RoutingModel(manager)
        # Add cost function
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        # Add generic dimension
        distances = [
            model.RegisterTransitCallback(One),
            model.RegisterTransitCallback(Two),
            model.RegisterTransitCallback(Three)
        ]
        model.AddDimensionWithVehicleTransits(distances, 90, 90, True,
                                              'distance')
        distance_dimension = model.GetDimensionOrDie('distance')
        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE)
        assignment = model.SolveWithParameters(search_parameters)
        self.assertEqual(90, assignment.ObjectiveValue())
        # Inspect solution
        for vehicle in range(0, model.vehicles()):
            node = model.Start(vehicle)
            cumul = 0
            while not model.IsEnd(node):
                self.assertEqual(cumul,
                                 assignment.Min(
                                     distance_dimension.CumulVar(node)))
                next_node = assignment.Value(model.NextVar(node))
                # Increment cumul by the vehicle distance which is equal to the vehicle
                # index + 1, cf. distances.
                cumul += vehicle + 1
                node = next_node

    def testConstantTSP(self):
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(10, 3, 0)
        model = pywrapcp.RoutingModel(manager)
        # Add cost function
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        # Add constant dimension
        model.AddConstantDimension(1, 100, True, 'count')
        count_dimension = model.GetDimensionOrDie('count')
        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE)
        assignment = model.SolveWithParameters(search_parameters)
        self.assertEqual(90, assignment.ObjectiveValue())
        # Inspect solution
        node = model.Start(0)
        count = 0
        while not model.IsEnd(node):
            self.assertEqual(count,
                             assignment.Value(count_dimension.CumulVar(node)))
            count += 1
            node = assignment.Value(model.NextVar(node))
        self.assertEqual(10, count)

    def testVectorTSP(self):
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(10, 3, 0)
        model = pywrapcp.RoutingModel(manager)
        # Add cost function
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        # Add vector dimension
        values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        model.AddVectorDimension(values, 100, True, 'vector')
        vector_dimension = model.GetDimensionOrDie('vector')
        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE)
        assignment = model.SolveWithParameters(search_parameters)
        self.assertEqual(90, assignment.ObjectiveValue())
        # Inspect solution
        node = model.Start(0)
        cumul = 0
        while not model.IsEnd(node):
            self.assertEqual(cumul,
                             assignment.Value(vector_dimension.CumulVar(node)))
            cumul += values[node]
            node = assignment.Value(model.NextVar(node))

    def testMatrixTSP(self):
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(5, 1, 0)
        model = pywrapcp.RoutingModel(manager)
        # Add cost function
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        # Add vector dimension
        values = [(0, 0, 0, 0, 0), (1, 1, 1, 1, 1), (2, 2, 2, 2, 2),
                  (3, 3, 3, 3, 3), (4, 4, 4, 4, 4)]
        model.AddMatrixDimension(values, 100, True, 'matrix')
        dimension = model.GetDimensionOrDie('matrix')
        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE)
        assignment = model.SolveWithParameters(search_parameters)
        self.assertEqual(20, assignment.ObjectiveValue())
        # Inspect solution
        node = model.Start(0)
        cumul = 0
        while not model.IsEnd(node):
            self.assertEqual(cumul, assignment.Value(dimension.CumulVar(node)))
            cumul += values[node][node]
            node = assignment.Value(model.NextVar(node))

    def testDisjunctionTSP(self):
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(5, 1, 0)
        model = pywrapcp.RoutingModel(manager)
        # Add cost function
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        # Add disjunctions
        disjunctions = [[manager.NodeToIndex(1),
                         manager.NodeToIndex(2)], [manager.NodeToIndex(3)]
                        ]
        # for disjunction in disjunctions:
        #     model.AddDisjunction(disjunction, 8)
        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        assignment = model.SolveWithParameters(search_parameters)
        # self.assertEqual(8, assignment.ObjectiveValue())
        # Inspect solution
        node = model.Start(0)
        count = 0
        while not model.IsEnd(node):
            count += 1
            node = assignment.Value(model.NextVar(node))
        # self.assertEqual(3, count)

        # Inspect solution
        index = model.Start(0)
        visited_nodes = []
        expected_visited_nodes = [1, 2, 3, 4, 0]
        while not model.IsEnd(index):
            index = assignment.Value(model.NextVar(index))
            visited_nodes.append(manager.IndexToNode(index))
        self.assertEqual(expected_visited_nodes, visited_nodes)

    def testDisjunctionPenaltyTSP(self):
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(5, 1, 0)
        model = pywrapcp.RoutingModel(manager)
        # Add cost function
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        # Add disjunctions
        disjunctions = [
            # ([manager.NodeToIndex(1), manager.NodeToIndex(2)], 10000),
            ([manager.NodeToIndex(2)], 4),
            ([manager.NodeToIndex(3)], 6),
            ([manager.NodeToIndex(4)], 10000)
        ]
        for disjunction, penalty in disjunctions:
            model.AddDisjunction(disjunction, penalty)
        # Solve
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE)
        assignment = model.SolveWithParameters(search_parameters)
        self.assertEqual(pywrapcp.RoutingModel.ROUTING_SUCCESS, model.status())
        # self.assertEqual(68, assignment.ObjectiveValue())

        # Inspect solution
        node = model.Start(0)
        count = 0
        while not model.IsEnd(node):
            count += 1
            node = assignment.Value(model.NextVar(node))
        # self.assertEqual(8, count)

        # Inspect solution
        index = model.Start(0)
        visited_nodes = []
        expected_visited_nodes = [1, 2, 3, 4, 0]
        while not model.IsEnd(index):
            index = assignment.Value(model.NextVar(index))
            visited_nodes.append(manager.IndexToNode(index))
        self.assertEqual(expected_visited_nodes, visited_nodes)

    def testRoutingModelParameters(self):
        # Create routing model with parameters
        parameters = pywrapcp.DefaultRoutingModelParameters()
        parameters.solver_parameters.CopyFrom(
            pywrapcp.Solver.DefaultSolverParameters())
        parameters.solver_parameters.trace_propagation = True
        manager = pywrapcp.RoutingIndexManager(10, 1, 0)
        model = pywrapcp.RoutingModel(manager, parameters)
        self.assertEqual(1, model.vehicles())
        self.assertTrue(model.solver().Parameters().trace_propagation)

    def testRoutingLocalSearchFiltering(self):
        parameters = pywrapcp.DefaultRoutingModelParameters()
        parameters.solver_parameters.profile_local_search = True
        manager = pywrapcp.RoutingIndexManager(10, 1, 0)
        model = pywrapcp.RoutingModel(manager, parameters)
        model.Solve()
        profile = model.solver().LocalSearchProfile()
        print(profile)
        self.assertTrue(isinstance(profile, str))
        self.assertTrue(profile)  # Verify it's not empty.

    def testRoutingSearchParameters(self):
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(10, 1, 0)
        model = pywrapcp.RoutingModel(manager)
        # Add cost function
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        # Close with parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.SAVINGS)
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        search_parameters.local_search_operators.use_two_opt = (
            pywrapcp.BOOL_FALSE)
        search_parameters.solution_limit = 20
        model.CloseModelWithParameters(search_parameters)
        # Solve with parameters
        assignment = model.SolveWithParameters(search_parameters)
        self.assertEqual(
            10, model.GetNumberOfDecisionsInFirstSolution(search_parameters))
        self.assertEqual(
            0, model.GetNumberOfRejectsInFirstSolution(search_parameters))
        self.assertEqual(90, assignment.ObjectiveValue())
        assignment = model.SolveFromAssignmentWithParameters(
            assignment, search_parameters)
        self.assertEqual(90, assignment.ObjectiveValue())

    def testFindErrorInRoutingSearchParameters(self):
        params = pywrapcp.DefaultRoutingSearchParameters()
        params.local_search_operators.use_cross = pywrapcp.BOOL_UNSPECIFIED
        self.assertIn('cross',
                      pywrapcp.FindErrorInRoutingSearchParameters(params))

    def testCallback(self):
        manager = pywrapcp.RoutingIndexManager(10, 1, 0)
        model = pywrapcp.RoutingModel(manager)
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        callback = Callback(model)
        model.AddAtSolutionCallback(callback)
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        assignment = model.SolveWithParameters(search_parameters)
        self.assertEqual(90, assignment.ObjectiveValue())
        self.assertEqual(1, len(callback.costs))
        self.assertEqual(90, callback.costs[0])

    def testReadAssignment(self):
        manager = pywrapcp.RoutingIndexManager(10, 2, 0)
        model = pywrapcp.RoutingModel(manager)
        # TODO(user): porting this segfaults the tests.
        cost = model.RegisterTransitCallback(partial(TransitDistance, manager))
        model.SetArcCostEvaluatorOfAllVehicles(cost)
        routes = [[
            manager.NodeToIndex(1),
            manager.NodeToIndex(3),
            manager.NodeToIndex(5),
            manager.NodeToIndex(4),
            manager.NodeToIndex(2),
            manager.NodeToIndex(6)
        ], [
            manager.NodeToIndex(7),
            manager.NodeToIndex(9),
            manager.NodeToIndex(8)
        ]]
        assignment = model.ReadAssignmentFromRoutes(routes, False)
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.solution_limit = 1
        solution = model.SolveFromAssignmentWithParameters(
            assignment, search_parameters)
        self.assertEqual(90, solution.ObjectiveValue())
        for vehicle in range(0, model.vehicles()):
            node = model.Start(vehicle)
            count = 0
            while not model.IsEnd(node):
                node = solution.Value(model.NextVar(node))
                if not model.IsEnd(node):
                    self.assertEqual(routes[vehicle][count],
                                     manager.IndexToNode(node))
                    count += 1


if __name__ == '__main__':
    unittest.main()
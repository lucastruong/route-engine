from src.problem.problem_location import PROBLEM_LOCATION_PICKUP, PROBLEM_LOCATION_DELIVERY
from src.problem.problem_options import create_options
from src.problem.problem_vehicle import create_problem_vehicle, ProblemVehicle
from src.problem.problem_visit import create_problem_visit, ProblemVisit


class ProblemAdapter:
    def __init__(self, problem: dict):
        self.problem = problem
        self.callback_url = problem.get('callback_url')
        self.visits: list[ProblemVisit] = []
        self.vehicles: list[ProblemVehicle] = []
        self.options = create_options(problem.get('options', {}))
        self.pickups_deliveries = []
        self.force_order = False

    def transform_routific(self):
        self._reformat_visits()
        self._reformat_fleets()

    def _reformat_visits(self):
        def create_visit(key_visit, visit_json, location_key, location_type):
            visit_json = create_problem_visit(key_visit, visit_json, location_key, location_type)
            self.visits.append(visit_json)

        visits = self.problem.get('visits')
        for key in visits:
            visit = visits[key]

            # Create pickup
            visit_pickup = visit.get('pickup')
            visit_pickup_key = key + '_' + PROBLEM_LOCATION_PICKUP
            if visit_pickup is not None:
                create_visit(key, visit_pickup, visit_pickup_key, PROBLEM_LOCATION_PICKUP)

            # Create delivery
            visit_delivery = visit.get('dropoff')
            visit_delivery_key = key + '_' + PROBLEM_LOCATION_DELIVERY
            if visit_delivery is not None:
                create_visit(key, visit_delivery, visit_delivery_key, PROBLEM_LOCATION_DELIVERY)
                self.pickups_deliveries.append([visit_pickup_key, visit_delivery_key])

            # Default visit for vrp
            if visit_pickup is None:
                create_visit(key, visit, key, PROBLEM_LOCATION_PICKUP)

    def _reformat_fleets(self):
        fleets = self.problem.get('fleet')
        for key in fleets:
            fleet = fleets[key]
            vehicle = create_problem_vehicle(key, fleet, self.options)

            # For vehicle orders
            for order_index in range(len(vehicle.order) - 1):
                orders = vehicle.order
                pickup_key = orders[order_index]
                delivery_key = orders[order_index + 1]
                self.pickups_deliveries.append([pickup_key, delivery_key])
                self.force_order = True

            self.vehicles.append(vehicle)

from src.problem.problem_options import ProblemOptions
from src.problem.problem_vehicle import create_problem_vehicle, ProblemVehicle
from src.problem.problem_visit import create_problem_visit, ProblemVisit


def create_options(options: dict):
    return ProblemOptions(options.get('balance', False), options.get('speed', 30))


class ProblemAdapter:
    def __init__(self, problem: dict):
        self.problem = problem
        self.callback_url = problem.get('callback_url')
        self.visits: list[ProblemVisit] = []
        self.vehicles: list[ProblemVehicle] = []
        self.options = create_options(problem.get('options', {}))

    def transform_routific(self):
        self._reformat_visits()
        self._reformat_fleets()

    def _reformat_visits(self):
        visits = self.problem.get('visits')
        for key in visits:
            visit = visits[key]
            visit = create_problem_visit(key, visit)
            self.visits.append(visit)

    def _reformat_fleets(self):
        fleets = self.problem.get('fleet')
        for key in fleets:
            fleet = fleets[key]
            vehicle = create_problem_vehicle(key, fleet)
            self.vehicles.append(vehicle)

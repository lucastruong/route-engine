import sys

from src.problem.problem_capacity import ProblemCapacity
from src.problem.problem_location import ProblemLocation, create_problem_location
from src.problem.problem_options import ProblemOptions
from src.problem.problem_skill import ProblemSkill
from src.problem.problem_speed import create_speed, ProblemSpeed
from src.problem.problem_time import ProblemTime


def create_problem_vehicle(key: str, fleet: dict, options: ProblemOptions):
    start_location = fleet.get('start_location')
    key_start = start_location.get('id', key)
    start_location = create_problem_location(key_start, start_location)

    end_location = fleet.get('end_location', None)
    if end_location is not None:
        key_end = end_location.get('id', key + '_end')
        end_location = create_problem_location(key_end, end_location)

    start_time = ProblemTime(fleet.get('shift_start'))
    end_time = ProblemTime(fleet.get('shift_end'), '99:99')
    capacities = ProblemCapacity(fleet.get('capacity'), sys.maxsize)
    skills = ProblemSkill(fleet.get('type'))
    speed = create_speed(fleet.get('speed', options.speed.traffic))
    order = fleet.get('order', [])

    return ProblemVehicle(
        key, start_location, end_location,
        start_time, end_time,
        capacities, skills,
        speed, order
    )


class ProblemVehicle:
    def __init__(self, key: str,
                 start_location: ProblemLocation,
                 end_location: [ProblemLocation, None],
                 start_time: ProblemTime, end_time: ProblemTime,
                 capacities: ProblemCapacity, skills: ProblemSkill,
                 speed: ProblemSpeed,
                 order: list
                 ):
        self.id = key
        self.location = start_location
        self.end_location = end_location
        self.start_time = start_time
        self.end_time = end_time
        self.capacities = capacities
        self.skills = skills
        self.speed = speed
        self.order = order

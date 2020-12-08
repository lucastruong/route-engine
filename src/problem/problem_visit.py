from src.problem.problem_capacity import ProblemCapacity
from src.problem.problem_location import ProblemLocation, create_problem_location
from src.problem.problem_skill import ProblemSkill
from src.problem.problem_time import ProblemTime
from src.problem.problem_duration import ProblemDuration


def create_problem_visit(key: str, visit: dict):
    location = create_problem_location(key, visit.get('location'))
    start_time = ProblemTime(visit.get('start'))
    end_time = ProblemTime(visit.get('end'), '99:99')
    duration = ProblemDuration(visit.get('duration'))
    capacities = ProblemCapacity(visit.get('load'))
    skills = ProblemSkill(visit.get('type'))
    return ProblemVisit(key, location, start_time, end_time, duration, capacities, skills)


class ProblemVisit:
    def __init__(self, key: str, location: ProblemLocation,
                 start_time: ProblemTime, end_time: ProblemTime, duration: ProblemDuration,
                 loads: ProblemCapacity, skills: ProblemSkill
                 ):
        self.id = key
        self.location = location
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.loads = loads
        self.required_skills = skills

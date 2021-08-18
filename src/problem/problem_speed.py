from src.problem.problem_helper import kmph_to_mps

costs = {
    'faster': 1.5, 'fast': 1.25,
    'normal': 1,
    'slow': 0.75, 'very slow': 0.5,
    'bike': 0.8,
}


def create_speed(setting: str):
    traffic = 'normal'
    if setting in costs:
        traffic = setting

    return ProblemSpeed(traffic)


class ProblemSpeed:
    def __init__(self, traffic: str):
        speed_base = 32  # 32 km/h
        self.traffic = traffic
        self.cost = costs.get(self.traffic)
        self.kmh = speed_base * self.cost
        self.mps = kmph_to_mps(self.kmh)  # To meters per seconds

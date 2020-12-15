from src.problem.problem_speed import ProblemSpeed, create_speed


def create_options(options: dict):
    balance = options.get('balance', False)
    speed = create_speed(options.get('traffic', 'normal'))
    return ProblemOptions(speed, balance)


class ProblemOptions:
    def __init__(self, speed: ProblemSpeed, balance: bool = False):
        self.speed = speed
        self.balance = balance

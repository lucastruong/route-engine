class ProblemDuration:
    def __init__(self, minutes: int):
        duration = minutes
        if minutes is None:
            duration = 0
        self.minutes = int(duration)

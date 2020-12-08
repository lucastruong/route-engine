class ProblemSkill:
    def __init__(self, items):
        demands = []
        if type(items) == list:
            for value in items:
                demands.append('SKILL_' + value.upper())
        elif type(items) == str:
            demands.append('SKILL_' + str(items))
        self.demands = demands

    def __get__(self, instance, owner):
        return self.demands

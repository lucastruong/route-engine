class ProblemCapacity:
    def __init__(self, items, default=0):
        demands = {}
        if items is None:
            demands['CAP_DEFAULT'] = default
        elif type(items) == dict:
            for key, value in items.items():
                demands['CAP_' + str(key).upper()] = int(value)
        else:
            demands['CAP_DEFAULT'] = int(items)
        self.demands = demands

    def __get__(self, instance, owner):
        return self.demands

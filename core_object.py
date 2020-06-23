import datetime

class Location:
    def __init__(self, key, name, lat, lng):
        self.id = key
        self.name = name
        self.lat = float(lat)
        self.lng = float(lng)

class Time:
    def __init__(self, hhmm, default_hhmm='00:00'):
        time_str = hhmm
        if hhmm is None:
            time_str = default_hhmm
        try:
            time_obj = datetime.datetime.strptime(time_str, '%H:%M').time()
        except:
            time_obj = datetime.datetime.strptime(default_hhmm, '%H:%M').time()

        self.hhmm = time_obj.strftime('%H:%M')
        self.seconds = datetime.timedelta(
            hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second).total_seconds()
        self.seconds = int(self.seconds)

class Duration:
    def __init__(self, minutes):
        duration = minutes
        if minutes is None:
            duration = 0
        self.minutes = int(duration)

class Capacity:
    def __init__(self, items, default=0):
        demands = {}
        if items is None:
            demands['CAP_DEFAULT'] = default
        elif type(items) == dict:
            for key, value in items.items():
                demands[str(key).upper()] = int(value)
        else:
            demands['CAP_DEFAULT'] = int(items)
        self.demands = demands

    def __get__(self, instance, owner):
        return self.demands

class Skill:
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

class Visit:
    def __init__(self, key, location, start_time, end_time, duration, loads, required_skills):
        self.id = key
        self.location = location
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.loads = loads
        self.required_skills = required_skills

class Vehicle:
    def __init__(self, key, start_location, start_time, end_time, capacities, skills):
        self.id = key
        self.location = start_location
        self.start_time = start_time
        self.end_time = end_time
        self.capacities = capacities
        self.skills = skills

class Problem_Adapter:
    def __init__(self, problem):
        self.problem = problem
        self.callback_url = problem.get('callback_url')
        self.visits = []
        self.vehicles = []

    def _create_location(self, key, location):
        name = location.get('name')
        if name is None:
            name = key
        return Location(key, name, location.get('lat'), location.get('lng'))

    def transform_routific(self):
        self._routific_format_visits()
        self._routific_format_fleets()

    def _routific_format_visits(self):
        visits = self.problem.get('visits')
        for key in visits:
            visit = visits[key]
            visit = self._routific_format_visit(key, visit)
            self.visits.append(visit)

    def _routific_format_fleets(self):
        fleets = self.problem.get('fleet')
        for key in fleets:
            fleet = fleets[key]
            vehicle = self._routific_format_fleet(key, fleet)
            self.vehicles.append(vehicle)

    def _routific_format_visit(self, key, visit):
        location = self._create_location(key, visit.get('location'))
        start_time = Time(visit.get('start'))
        end_time = Time(visit.get('end'), '23:59')
        duration = Duration(visit.get('duration'))
        loads = Capacity(visit.get('load'))
        required_skills = Skill(visit.get('type'))
        return Visit(key, location, start_time, end_time, duration, loads, required_skills)

    def _routific_format_fleet(self, key, fleet):
        start_location = fleet.get('start_location')
        key_start = start_location.get('id')
        if key_start is None:
            key_start = key + '_start'
        start_location = self._create_location(key_start, start_location)

        start_time = Time(fleet.get('shift_start'))
        end_time = Time(fleet.get('shift_end'), '23:59')
        capacities = Capacity(fleet.get('capacity'), 99)
        skills = Skill(fleet.get('type'))
        return Vehicle(key, start_location, start_time, end_time, capacities, skills)

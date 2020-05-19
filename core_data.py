def create_data_all_locations(adapter):
    locations = []
    for vehicle in adapter.vehicles: locations.append(vehicle)
    for visit in adapter.visits: locations.append(visit)
    return locations

def create_data_locations(adapter):
    locations = []
    for vehicle in adapter.vehicles: locations.append((vehicle.location))
    for visit in adapter.visits: locations.append((visit.location))
    return locations

def create_data_times(adapter):
    times = []
    for vehicle in adapter.vehicles: times.append((vehicle.start_time, vehicle.end_time))
    for visit in adapter.visits: times.append((visit.start_time, visit.end_time))
    return times

def create_data_service_times(adapter):
    times = []
    for vehicle in adapter.vehicles: times.append(0)
    for visit in adapter.visits: times.append(visit.duration.minutes * 60)
    return times

def create_data_capacities(adapter):
    # Prepare the capacities global
    capacities = []
    for vehicle in adapter.vehicles:
        for capacity_key in vehicle.capacities.demands:
            if capacity_key not in capacities: capacities.append(capacity_key)
        for skill_key in vehicle.skills.demands:
            if skill_key not in capacities: capacities.append(skill_key)
    for visit in adapter.visits:
        for capacity_key in visit.loads.demands:
            if capacity_key not in capacities: capacities.append(capacity_key)
        for skill_key in visit.required_skills.demands:
            if skill_key not in capacities: capacities.append(skill_key)

    # Prepare the capacities of vehicles
    demands = {}
    vehicle_capacities = {}
    for capacity_key in capacities:
        sub_demands = []
        sub_vehicle_capacities = []

        for vehicle in adapter.vehicles:
            sub_demands.append(0)
            if capacity_key in vehicle.capacities.demands: sub_vehicle_capacities.append(vehicle.capacities.demands.get(capacity_key))
            elif capacity_key in vehicle.skills.demands: sub_vehicle_capacities.append(9999)
            else: sub_vehicle_capacities.append(0)

        for visit in adapter.visits:
            if capacity_key in visit.loads.demands: sub_demands.append(visit.loads.demands.get(capacity_key))
            elif capacity_key in visit.required_skills.demands: sub_demands.append(1)
            else: sub_demands.append(0)

        demands[capacity_key] = sub_demands
        vehicle_capacities[capacity_key] = sub_vehicle_capacities

    return {'capacities': capacities, 'demands': demands, 'vehicle_capacities': vehicle_capacities}

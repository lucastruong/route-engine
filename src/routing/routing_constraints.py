from functools import partial


def add_distance_constraint(routing, transit_callback_index):
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        99000,  # vehicle maximum travel distance (meters)
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(0)


def add_capacities_constraint(routing, manager, data):
    capacities = data['capacities']
    demands = data['demands']
    vehicle_capacities = data['vehicle_capacities']

    for capacity_key in capacities:
        sub_demands = demands.get(capacity_key)
        sub_vehicle_capacities = vehicle_capacities.get(capacity_key)

        demand_callback_index = routing.RegisterUnaryTransitCallback(
            partial(create_demand_callback(sub_demands), manager))

        capacity = 'Capacity' + capacity_key
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            sub_vehicle_capacities,  # vehicle maximum capacities
            True,  # start cumul to zero
            capacity)


def allow_drop_nodes(routing, manager, data):
    # Allow to drop nodes.
    penalty = 99000 # meters
    for node in range(1, len(data['distance_matrix'])):
        index = manager.NodeToIndex(node)
        routing.AddDisjunction([index], penalty)


def create_demand_callback(demands):
    # Add Capacity constraint.
    def demand_callback(manager, from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    return demand_callback


def add_time_window_constraints(routing, manager, data, time_evaluator_index):
    dimension_name = 'Time'
    routing.AddDimension(
        time_evaluator_index,
        24 * 60 * 60,  # allow waiting time
        24 * 60 * 60 * 7,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        dimension_name)
    time_dimension = routing.GetDimensionOrDie(dimension_name)

    # if (data['adapter'].options.balance):
    #     time_dimension.SetGlobalSpanCostCoefficient(100)

    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx < data['num_vehicles']:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add time window constraints for each vehicle start node.
    for vehicle_id in range(data['num_vehicles']):
        # Add time windows at start of routes
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(data['time_windows'][vehicle_id][0],
                                                data['time_windows'][vehicle_id][1])
        index = routing.End(vehicle_id)
        time_dimension.CumulVar(index).SetRange(data['time_windows'][vehicle_id][0],
                                                data['time_windows'][vehicle_id][1])

    # Instantiate route start and end times to produce feasible times.
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))




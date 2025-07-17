import itertools
from collections import namedtuple
from path_finder import DijkstraFind

Edge = namedtuple('Edge', ['to', 'cost', 'duration', 'transport_type', 'type', 'departure_time', 'arrival_time', 'departure_date', 'arrival_date'])

def format_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def format_datetime(dt):
    """Format datetime object to string"""
    if hasattr(dt, 'strftime'):
        return dt.strftime('%Y-%m-%d %H:%M')
    else:
        # Fallback for time-only values
        return format_time(dt)

def path_str_with_departures(graph, path):
    segments = []
    current_time = 0  # Start at midnight
    current_date = None  # Track current date
    
    for i in range(len(path) - 1):
        from_node = path[i]
        to_node = path[i + 1]
        edges = [e for e in graph[from_node] if e.to == to_node]
        if not edges:
            segments.append(f"{from_node} (N/A)")
            continue
        edge = min(edges, key=lambda e: e.cost)
        
        if edge.type == 'fixed':
            if hasattr(edge.departure_time, 'strftime'):
                # Flight with datetime
                dep = format_datetime(edge.departure_time)
                current_date = edge.arrival_date
                current_time = edge.arrival_time.hour * 60 + edge.arrival_time.minute
            else:
                # Local transport with time only
                dep = format_time(edge.departure_time)
                current_time = edge.arrival_time
            segments.append(f"{from_node} ({dep})")
        else:  # flexible
            # Calculate actual departure time based on current arrival time
            departure_time = DijkstraFind.calculate_next_departure_time(edge.departure_time, current_time)
            if departure_time is not None:
                dep = format_time(departure_time)
                segments.append(f"{from_node} ({dep})")
                current_time = departure_time + edge.duration
            else:
                segments.append(f"{from_node} (no service)")
    
    segments.append(path[-1])  # Last node, no departure time
    return ' -> '.join(segments)

def compute_best_round_trip(graph):
    # Option 1: Home -> Florence -> Rome -> Home
    path1_1, cost1_1, dur1_1 = DijkstraFind.find_best_path(graph, None, start='Home', end='Florence')
    path1_2, cost1_2, dur1_2 = DijkstraFind.find_best_path(graph, None, start='Florence', end='Rome')
    path1_3, cost1_3, dur1_3 = DijkstraFind.find_best_path(graph, None, start='Rome', end='Home')
    total_cost1 = cost1_1 + cost1_2 + cost1_3
    total_dur1 = dur1_1 + dur1_2 + dur1_3
    full_path1 = path1_1 + path1_2[1:] + path1_3[1:]

    # Option 2: Home -> Rome -> Florence -> Home
    path2_1, cost2_1, dur2_1 = DijkstraFind.find_best_path(graph, None, start='Home', end='Rome')
    path2_2, cost2_2, dur2_2 = DijkstraFind.find_best_path(graph, None, start='Rome', end='Florence')
    path2_3, cost2_3, dur2_3 = DijkstraFind.find_best_path(graph, None, start='Florence', end='Home')
    total_cost2 = cost2_1 + cost2_2 + cost2_3
    total_dur2 = dur2_1 + dur2_2 + dur2_3
    full_path2 = path2_1 + path2_2[1:] + path2_3[1:]

    print('\n--- Round Trip Options ---')
    print('Option 1: Home -> Florence -> Rome -> Home')
    print('   Path:', path_str_with_departures(graph, full_path1))
    print(f'   Total cost: £{total_cost1}, duration: {total_dur1} minutes')
    print('Option 2: Home -> Rome -> Florence -> Home')
    print('   Path:', path_str_with_departures(graph, full_path2))
    print(f'   Total cost: £{total_cost2}, duration: {total_dur2} minutes')

    if total_cost1 < total_cost2:
        print('\nRecommended: Option 1 (Home -> Florence -> Rome -> Home)')
    elif total_cost2 < total_cost1:
        print('\nRecommended: Option 2 (Home -> Rome -> Florence -> Home)')
    else:
        print('\nBoth options have the same total cost. Choose based on duration or preference.') 
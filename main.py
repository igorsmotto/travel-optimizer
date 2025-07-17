import sys
from collections import defaultdict
from travel_graph import Edge, compute_best_round_trip
from path_finder import DijkstraFind
from parsing_utils import parse_cost, parse_duration, parse_time, parse_flexible_schedule, parse_datetime, datetime_to_minutes_since_midnight

def split_and_strip(from_to, separator):
    """Split a string by separator and strip whitespace from each part."""
    return [x.strip() for x in from_to.split(separator)]

def create_edge(to_node, cost, duration, transport_type, edge_type, departure, arrival):
    """Create an Edge object with the given parameters."""
    if edge_type == 'fixed':
        # Check if this is a flight (has datetime) or local transport (time only)
        departure_dt = parse_datetime(departure)
        arrival_dt = parse_datetime(arrival)

        if hasattr(departure_dt, 'strftime') and hasattr(arrival_dt, 'strftime'):
            # Flight with datetime
            return Edge(
                to=to_node,
                cost=parse_cost(cost),
                duration=parse_duration(duration),
                transport_type=transport_type,
                type='fixed',
                departure_time=departure_dt,
                arrival_time=arrival_dt,
                departure_date=departure_dt.date(),
                arrival_date=arrival_dt.date()
            )
        else:
            # Local transport with time only
            return Edge(
                to=to_node,
                cost=parse_cost(cost),
                duration=parse_duration(duration),
                transport_type=transport_type,
                type='fixed',
                departure_time=departure_dt,
                arrival_time=arrival_dt,
                departure_date=None,
                arrival_date=None
            )
    else:  # flexible
        schedule = parse_flexible_schedule(departure)
        return Edge(
            to=to_node,
            cost=parse_cost(cost),
            duration=parse_duration(duration),
            transport_type=transport_type,
            type='flexible',
            departure_time=schedule,  # Store schedule dict
            arrival_time=None,  # Will be calculated dynamically
            departure_date=None,
            arrival_date=None
        )

def build_graph_from_file(filename):
    graph = defaultdict(list)
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = [p.strip() for p in line.split('|')]
            if len(parts) != 7:
                continue
            from_to, cost, duration, transport_type, edge_type, departure, arrival = parts
            
            if '<->' in from_to:
                from_node, to_node = split_and_strip(from_to, '<->')
                is_bidirectional = True
            elif '->' in from_to:
                from_node, to_node = split_and_strip(from_to, '->')
                is_bidirectional = False
            elif '<-' in from_to:
                to_node, from_node = split_and_strip(from_to, '<-')
                is_bidirectional = False

            edge = create_edge(to_node, cost, duration, transport_type, edge_type, departure, arrival)
            
            graph[from_node].append(edge)
            
            if is_bidirectional:
                rev_edge = create_edge(from_node, cost, duration, transport_type, edge_type, departure, arrival)
                graph[to_node].append(rev_edge)

    return graph

def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py edges.txt')
        return

    filename = sys.argv[1]
    graph = build_graph_from_file(filename)

    compute_best_round_trip(graph)

if __name__ == '__main__':
    main() 
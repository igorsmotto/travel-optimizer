import heapq
from datetime import datetime, timedelta

class DijkstraFind:
    @staticmethod
    def calculate_next_departure_time(schedule, arrival_time):
        """Calculate the next available departure time for a flexible edge based on arrival time"""
        start_time = schedule['start_time']
        end_time = schedule['end_time']
        frequency = schedule['frequency']
        
        # If arrival time is before the schedule starts, use the first departure
        if arrival_time < start_time:
            return start_time
        
        # If arrival time is after the schedule ends, no departure available
        if arrival_time >= end_time:
            return None
        
        # Calculate the next departure time based on frequency
        time_since_start = arrival_time - start_time
        periods_passed = (time_since_start // frequency) + 1
        next_departure = start_time + (periods_passed * frequency)
        
        # Check if this departure is still within the schedule
        if next_departure <= end_time:
            return next_departure
        else:
            return None

    @staticmethod
    def get_time_value(time_obj):
        """Extract time value from either datetime object or minutes since midnight"""
        if hasattr(time_obj, 'hour'):
            # datetime object
            return time_obj.hour * 60 + time_obj.minute
        else:
            # minutes since midnight
            return time_obj

    @staticmethod
    def path_cost_and_duration(graph, path):
        total_cost = 0
        total_duration = 0
        current_time = 0  # Start at midnight
        current_date = None  # Track current date
        
        for i in range(len(path)-1):
            from_node = path[i]
            to_node = path[i+1]
            # Choose the edge with the lowest cost between from_node and to_node
            edges = [e for e in graph[from_node] if e.to == to_node]
            if not edges:
                return float('inf'), float('inf')
            edge = min(edges, key=lambda e: e.cost)
            
            # Calculate departure time for flexible edges
            if edge.type == 'flexible':
                departure_time = DijkstraFind.calculate_next_departure_time(edge.departure_time, current_time)
                if departure_time is None:
                    return float('inf'), float('inf')  # No available departure
                current_time = departure_time + edge.duration
            else:
                # For fixed edges, check if it's a flight with datetime
                if hasattr(edge.departure_time, 'strftime'):
                    # Flight with datetime
                    current_time = DijkstraFind.get_time_value(edge.arrival_time)
                    current_date = edge.arrival_date
                else:
                    # Local transport with time only
                    current_time = edge.arrival_time
            
            total_cost += edge.cost
            total_duration += edge.duration
        return total_cost, total_duration

    @staticmethod
    def find_best_path(graph, must_visit, start='Home', end=None):
        if end is None:
            raise ValueError('End node must be specified for DijkstraFind')
        
        # Priority queue: (total_cost, current_time, current_date, node, path)
        queue = [(0, 0, None, start, [start])]  # Start at midnight (0 minutes)
        visited = {}
        best_path = None
        best_cost = float('inf')
        best_duration = float('inf')
        
        while queue:
            cost, current_time, current_date, node, path = heapq.heappop(queue)
            
            # Skip if we've found a better path to this node
            if (node in visited and visited[node] <= cost):
                continue
            visited[node] = cost
            
            if node == end:
                if cost < best_cost:
                    best_cost = cost
                    # Calculate actual duration including waiting times
                    actual_duration = DijkstraFind.calculate_path_duration(graph, path)
                    best_duration = actual_duration
                    best_path = path
                continue
            
            for edge in graph.get(node, []):
                if edge.to not in path:  # avoid cycles
                    # Calculate departure time for flexible edges
                    if edge.type == 'flexible':
                        departure_time = DijkstraFind.calculate_next_departure_time(edge.departure_time, current_time)
                        if departure_time is None:
                            continue  # No available departure, skip this edge
                        new_time = departure_time + edge.duration
                        new_date = current_date
                    else:
                        # For fixed edges, check if it's a flight with datetime
                        if hasattr(edge.departure_time, 'strftime'):
                            # Flight with datetime - check if we can take this flight
                            if current_date is not None and edge.departure_date < current_date:
                                continue  # Flight has already departed
                            departure_time = DijkstraFind.get_time_value(edge.departure_time)
                            new_time = DijkstraFind.get_time_value(edge.arrival_time)
                            new_date = edge.arrival_date
                        else:
                            # Local transport with time only
                            departure_time = edge.departure_time
                            new_time = edge.arrival_time
                            new_date = current_date
                    
                    heapq.heappush(queue, (cost + edge.cost, new_time, new_date, edge.to, path + [edge.to]))
        
        return best_path, best_cost, best_duration

    @staticmethod
    def calculate_path_duration(graph, path):
        """Calculate the actual duration of a path including waiting times"""
        if not path or len(path) < 2:
            return 0
        
        total_duration = 0
        current_time = 0  # Start at midnight
        current_date = None  # Track current date
        
        for i in range(len(path) - 1):
            from_node = path[i]
            to_node = path[i + 1]
            edges = [e for e in graph[from_node] if e.to == to_node]
            if not edges:
                return float('inf')
            edge = min(edges, key=lambda e: e.cost)
            
            if edge.type == 'flexible':
                departure_time = DijkstraFind.calculate_next_departure_time(edge.departure_time, current_time)
                if departure_time is None:
                    return float('inf')
                # Add waiting time
                waiting_time = departure_time - current_time
                total_duration += waiting_time + edge.duration
                current_time = departure_time + edge.duration
            else:
                # For fixed edges, check if it's a flight with datetime
                if hasattr(edge.departure_time, 'strftime'):
                    # Flight with datetime
                    departure_time = DijkstraFind.get_time_value(edge.departure_time)
                    if current_time < departure_time:
                        waiting_time = departure_time - current_time
                        total_duration += waiting_time
                    total_duration += edge.duration
                    current_time = DijkstraFind.get_time_value(edge.arrival_time)
                    current_date = edge.arrival_date
                else:
                    # Local transport with time only
                    if current_time < edge.departure_time:
                        waiting_time = edge.departure_time - current_time
                        total_duration += waiting_time
                    total_duration += edge.duration
                    current_time = edge.arrival_time
        
        return total_duration 
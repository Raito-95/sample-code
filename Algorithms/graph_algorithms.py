"""Graph algorithms including BFS, Dijkstra's algorithm, and A* search."""

from collections import deque
import heapq


def bfs_shortest_path(graph, start, goal):
    """Return the shortest path between start and goal using BFS.

    Args:
        graph (dict): Mapping of node -> list of neighbor nodes.
        start (hashable): Starting node.
        goal (hashable): Goal node.

    Returns:
        list or None: List of nodes representing the path, or None if unreachable.
    """
    visited = set([start])
    queue = deque([(start, [start])])

    while queue:
        node, path = queue.popleft()
        if node == goal:
            return path
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None


def dijkstra_shortest_paths(graph, start):
    """Compute shortest path distances from start to all nodes.

    Args:
        graph (dict): Mapping of node -> dict of neighbor -> weight.
        start (hashable): Starting node.

    Returns:
        dict: Mapping of node -> distance from start.
    """
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    pq = [(0, start)]

    while pq:
        current_distance, current_node = heapq.heappop(pq)
        if current_distance > distances[current_node]:
            continue
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    return distances


def astar_shortest_path(graph, start, goal, heuristic):
    """Return the shortest path between start and goal using A* search.

    Args:
        graph (dict): Mapping of node -> dict of neighbor -> weight.
        start (hashable): Starting node.
        goal (hashable): Goal node.
        heuristic (callable): Function h(node) -> estimated cost from node to goal.

    Returns:
        list or None: List of nodes representing the path, or None if unreachable.
    """
    open_set = [(heuristic(start), 0, start, [start])]
    visited = {}

    while open_set:
        est_total, cost_so_far, node, path = heapq.heappop(open_set)
        if node == goal:
            return path
        if node in visited and visited[node] <= cost_so_far:
            continue
        visited[node] = cost_so_far
        for neighbor, weight in graph.get(node, {}).items():
            new_cost = cost_so_far + weight
            heapq.heappush(
                open_set,
                (new_cost + heuristic(neighbor), new_cost, neighbor, path + [neighbor]),
            )
    return None


if __name__ == "__main__":
    example_graph = {
        "A": ["B", "C"],
        "B": ["D", "E"],
        "C": ["F"],
        "D": [],
        "E": ["F"],
        "F": [],
    }
    print("BFS path:", bfs_shortest_path(example_graph, "A", "F"))

    weighted_graph = {
        "A": {"B": 1, "C": 4},
        "B": {"C": 2, "D": 5},
        "C": {"D": 1},
        "D": {},
    }
    print("Dijkstra distances:", dijkstra_shortest_paths(weighted_graph, "A"))
    print(
        "A* path:",
        astar_shortest_path(weighted_graph, "A", "D", lambda n: 0),
    )

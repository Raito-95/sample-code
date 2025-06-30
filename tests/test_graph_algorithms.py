from Algorithms.graph_algorithms import bfs_shortest_path, dijkstra_shortest_paths


def test_bfs_shortest_path():
    graph = {
        "A": ["B", "C"],
        "B": ["D", "E"],
        "C": ["F"],
        "D": [],
        "E": ["F"],
        "F": [],
    }
    assert bfs_shortest_path(graph, "A", "F") == ["A", "C", "F"]


def test_dijkstra_shortest_paths():
    graph = {
        "A": {"B": 1, "C": 4},
        "B": {"C": 2, "D": 5},
        "C": {"D": 1},
        "D": {},
    }
    distances = dijkstra_shortest_paths(graph, "A")
    assert distances["D"] == 4
    assert distances["C"] == 3
    assert distances["B"] == 1

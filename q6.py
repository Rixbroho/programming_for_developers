import math
import heapq

# Safety probabilities for directed edges
SAFETY = {
    ("KTM","JA"): 0.90, ("KTM","JB"): 0.80,
    ("JA","KTM"): 0.90, ("JA","PH"):  0.95,
    ("JA","BS"):  0.70, ("JB","KTM"): 0.80,
    ("JB","JA"):  0.60, ("JB","BS"):  0.90,
    ("PH","JA"):  0.95, ("PH","BS"):  0.85,
    ("BS","JA"):  0.70, ("BS","JB"):  0.90,
    ("BS","PH"):  0.85,
}

def safest_path(safety_map, start, goal):
    """
    Find safest path using Dijkstra on -log(p) transformed weights.
    Returns (path, safety_probability).
    """
    # Build adjacency list with transformed weights
    graph = {}
    for (u, v), prob in safety_map.items():
        graph.setdefault(u, []).append((v, -math.log(prob)))

    dist   = {start: 0.0}
    parent = {start: None}
    pq     = [(0.0, start)]    # (transformed_cost, node)

    while pq:
        d, u = heapq.heappop(pq)
        if u == goal:
            break
        if d > dist.get(u, float("inf")):
            continue   # Stale entry
        for v, w in graph.get(u, []):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v]   = nd
                parent[v] = u
                heapq.heappush(pq, (nd, v))

    # Reconstruct path
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = parent.get(node)
    path.reverse()

    # Compute actual safety probability
    safety = 1.0
    for i in range(len(path) - 1):
        safety *= safety_map[(path[i], path[i+1])]

    return path, round(safety, 5)

path, safety = safest_path(SAFETY, "KTM", "BS")
print(f"Safest path: {' -> '.join(path)}")
print(f"Safety probability: {safety:.5f} ({safety*100:.2f}%)")
# Output: Safest path: KTM -> JA -> PH -> BS
# Safety probability: 0.72675 (72.68%)

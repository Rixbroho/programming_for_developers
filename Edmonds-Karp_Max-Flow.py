from collections import deque

# Capacity graph (trucks/hour)
def build_capacity():
    cap = {n: {} for n in ["KTM","JA","JB","PH","BS"]}
    edges = [
        ("KTM","JA",10), ("KTM","JB",15),
        ("JA","KTM",10), ("JA","PH",8),
        ("JA","BS",5),   ("JB","KTM",15),
        ("JB","JA",4),   ("JB","BS",12),
        ("PH","JA",8),   ("PH","BS",6),
        ("BS","JA",5),   ("BS","JB",12),
        ("BS","PH",6),
    ]
    for u, v, c in edges:
        cap[u][v] = cap[u].get(v, 0) + c
        cap[v].setdefault(u, 0)   # Ensure reverse edge exists
    return cap

def edmonds_karp(cap, source, sink):
    """
    Edmonds-Karp (BFS-based Ford-Fulkerson).
    Returns maximum flow from source to sink.
    """
    max_flow = 0

    while True:
        # BFS to find shortest augmenting path in residual graph
        parent = {source: None}
        queue  = deque([(source, float("inf"))])

        found_flow = 0
        while queue and not found_flow:
            u, pushed = queue.popleft()
            for v, capacity in cap[u].items():
                if v not in parent and capacity > 0:
                    parent[v] = u
                    flow = min(pushed, capacity)
                    if v == sink:
                        found_flow = flow
                        # Augment along path
                        node = sink
                        while node != source:
                            prev = parent[node]
                            cap[prev][node] -= flow
                            cap[node][prev] = cap[node].get(prev, 0) + flow
                            node = prev
                        break
                    queue.append((v, flow))

        if not found_flow:
            break    # No augmenting path found
        max_flow += found_flow

    return max_flow

cap = build_capacity()
result = edmonds_karp(cap, "KTM", "BS")
print(f"Maximum trucks/hour from KTM to BS: {result}")
# Expected output: 23

from math import gcd
from collections import defaultdict

def max_points_on_line(points):
    n = len(points)
    if n <= 2:
        return n

    best = 1
    for i in range(n):
        slopes = defaultdict(int)
        dup = 1      # count the anchor itself
        local = 0

        x1, y1 = points[i]
        for j in range(i + 1, n):
            x2, y2 = points[j]
            dx, dy = x2 - x1, y2 - y1

            # Handle duplicate points
            if dx == 0 and dy == 0:
                dup += 1
                continue

            # Reduce slope to lowest terms using GCD
            g = gcd(abs(dx), abs(dy))
            dx //= g
            dy //= g

            # Normalise sign so same slope maps to one key
            if dx < 0:
                dx, dy = -dx, -dy
            if dx == 0:
                dy = 1
            if dy == 0:
                dx = 1

            slopes[(dy, dx)] += 1
            local = max(local, slopes[(dy, dx)])

        # dup accounts for the anchor + any identical points
        best = max(best, local + dup)

    return best

    # Test 1: All three points are collinear (diagonal line)
print(max_points_on_line([[1,1],[2,2],[3,3]]))       # Expected: 3

# Test 2: Best line covers 4 of the 6 points
print(max_points_on_line([[1,1],[3,2],[5,3],[4,1],[2,3],[1,4]]))  # Expected: 4

# Test 3: Duplicate points should be included
print(max_points_on_line([[0,0],[0,0],[1,1]]))        # Expected: 3

# Test 4: Horizontal line scenario
print(max_points_on_line([[1,0],[2,0],[3,0],[4,1]]))  # Expected: 3


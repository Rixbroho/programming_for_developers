class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val   = val
        self.left  = left
        self.right = right

def max_path_sum(root):
    best = float("-inf")   # Handles all-negative trees

    def dfs(node):
        nonlocal best
        if not node:
            return 0

        # Clamp to 0: ignore a subtree if it reduces total
        left_gain  = max(0, dfs(node.left))
        right_gain = max(0, dfs(node.right))

        # Best path that bends at this node (uses both children)
        path_val = node.val + left_gain + right_gain
        best = max(best, path_val)

        # Return the gain this node can contribute to its parent
        # (a path can only go in one direction upward)
        return node.val + max(left_gain, right_gain)

    dfs(root)
    return best
    # Test 1: Tree [1, 2, 3] -> path 2->1->3 = 6
root1 = TreeNode(1, TreeNode(2), TreeNode(3))
print(max_path_sum(root1))   # Expected: 6

# Test 2: Tree [-10, 9, 20, null, null, 15, 7] -> path 15->20->7 = 42
root2 = TreeNode(-10, TreeNode(9),
                 TreeNode(20, TreeNode(15), TreeNode(7)))
print(max_path_sum(root2))   # Expected: 42

# Test 3: Single negative node (must return the node itself)
root3 = TreeNode(-5)
print(max_path_sum(root3))   # Expected: -5

# Test 4: All negative values
root4 = TreeNode(-3, TreeNode(-1), TreeNode(-2))
print(max_path_sum(root4))   # Expected: -1


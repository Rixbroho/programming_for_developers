def word_break_all(user_query, marketing_keywords_dictionary):
    word_set = set(marketing_keywords_dictionary)
    n = len(user_query)
    memo = {}   # memo[i] = list of valid sentences from index i

    def dfs(i):
        # Return cached result if already computed
        if i in memo:
            return memo[i]
        # Base case: reached end of string successfully
        if i == n:
            return [""]

        results = []
        for j in range(i + 1, n + 1):
            word = user_query[i:j]
            if word in word_set:
                tails = dfs(j)
                for tail in tails:
                    if tail == "":
                        results.append(word)
                    else:
                        results.append(word + " " + tail)

        memo[i] = results
        return results

    return dfs(0)

    # Test 1: Two valid segmentations
print(word_break_all("nepaltrekkingguide",
    ["nepal", "trekking", "guide", "nepaltrekking"]))
# Expected: ["nepal trekking guide", "nepaltrekking guide"]

# Test 2: Three valid segmentations
print(word_break_all("visitkathmandunepal",
    ["visit", "kathmandu", "nepal", "visitkathmandu", "kathmandunepal"]))
# Expected: ["visit kathmandu nepal", "visitkathmandu nepal", "visit kathmandunepal"]

# Test 3: No valid segmentation exists
print(word_break_all("everesthikingtrail",
    ["everest", "hiking", "trek"]))
# Expected: []


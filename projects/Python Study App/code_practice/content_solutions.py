from __future__ import annotations

from bisect import bisect_left
from collections import Counter, defaultdict, deque
from heapq import heappop, heappush


class ListNode:
    def __init__(self, val: int = 0, next: "ListNode | None" = None):
        self.val = val
        self.next = next


class TreeNode:
    def __init__(self, val: int = 0, left: "TreeNode | None" = None, right: "TreeNode | None" = None):
        self.val = val
        self.left = left
        self.right = right


def pair_sum_indices(nums, target):
    seen = {}
    for index, value in enumerate(nums):
        partner = target - value
        if partner in seen:
            return [seen[partner], index]
        seen[value] = index
    return []


def valid_brackets(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for character in text:
        if character in "([{":
            stack.append(character)
        elif not stack or stack.pop() != pairs.get(character):
            return False
    return not stack


def binary_search_index(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        middle = (left + right) // 2
        if nums[middle] == target:
            return middle
        if nums[middle] < target:
            left = middle + 1
        else:
            right = middle - 1
    return -1


def reverse_linked_list(head):
    previous = None
    current = head
    while current:
        following = current.next
        current.next = previous
        previous = current
        current = following
    return previous


def merge_sorted_linked_lists(list1, list2):
    dummy = ListNode()
    tail = dummy
    while list1 and list2:
        if list1.val <= list2.val:
            tail.next = list1
            list1 = list1.next
        else:
            tail.next = list2
            list2 = list2.next
        tail = tail.next
    tail.next = list1 if list1 else list2
    return dummy.next


def max_single_trade_profit(prices):
    lowest = float("inf")
    best = 0
    for price in prices:
        lowest = min(lowest, price)
        best = max(best, price - lowest)
    return best


def normalized_palindrome(text):
    left, right = 0, len(text) - 1
    while left < right:
        while left < right and not text[left].isalnum():
            left += 1
        while left < right and not text[right].isalnum():
            right -= 1
        if text[left].lower() != text[right].lower():
            return False
        left += 1
        right -= 1
    return True


def merge_sorted_values(left, right):
    merged = []
    first = second = 0
    while first < len(left) and second < len(right):
        if left[first] <= right[second]:
            merged.append(left[first])
            first += 1
        else:
            merged.append(right[second])
            second += 1
    return merged + left[first:] + right[second:]


def tree_max_depth(root):
    if root is None:
        return 0
    return 1 + max(tree_max_depth(root.left), tree_max_depth(root.right))


def longest_unique_span(text):
    last_seen = {}
    left = best = 0
    for right, character in enumerate(text):
        if character in last_seen and last_seen[character] >= left:
            left = last_seen[character] + 1
        last_seen[character] = right
        best = max(best, right - left + 1)
    return best


def group_anagram_words(words):
    groups = defaultdict(list)
    for word in words:
        groups[tuple(sorted(word))].append(word)
    return list(groups.values())


def three_sum_zero(nums):
    nums = sorted(nums)
    answers = []
    for index in range(len(nums) - 2):
        if index and nums[index] == nums[index - 1]:
            continue
        left, right = index + 1, len(nums) - 1
        while left < right:
            total = nums[index] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                answers.append([nums[index], nums[left], nums[right]])
                left += 1
                right -= 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
    return answers


def days_until_warmer(temperatures):
    answer = [0] * len(temperatures)
    stack = []
    for index, temperature in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temperature:
            earlier = stack.pop()
            answer[earlier] = index - earlier
        stack.append(index)
    return answer


def rotated_array_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        middle = (left + right) // 2
        if nums[middle] == target:
            return middle
        if nums[left] <= nums[middle]:
            if nums[left] <= target < nums[middle]:
                right = middle - 1
            else:
                left = middle + 1
        elif nums[middle] < target <= nums[right]:
            left = middle + 1
        else:
            right = middle - 1
    return -1


def merge_intervals(intervals):
    if not intervals:
        return []
    intervals = sorted(intervals)
    merged = [intervals[0][:]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def tree_level_order(root):
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result


def is_valid_bst(root):
    def valid(node, lower, upper):
        if not node:
            return True
        if not lower < node.val < upper:
            return False
        return valid(node.left, lower, node.val) and valid(node.right, node.val, upper)

    return valid(root, float("-inf"), float("inf"))


def count_islands(grid):
    if not grid:
        return 0
    rows, columns = len(grid), len(grid[0])
    visited = set()

    def visit(start_row, start_column):
        queue = deque([(start_row, start_column)])
        visited.add((start_row, start_column))
        while queue:
            row, column = queue.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = row + dr, column + dc
                if 0 <= nr < rows and 0 <= nc < columns and grid[nr][nc] == "1" and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))

    islands = 0
    for row in range(rows):
        for column in range(columns):
            if grid[row][column] == "1" and (row, column) not in visited:
                islands += 1
                visit(row, column)
    return islands


def shortest_clear_path(grid):
    if not grid or grid[0][0] or grid[-1][-1]:
        return -1
    rows, columns = len(grid), len(grid[0])
    queue = deque([(0, 0, 1)])
    visited = {(0, 0)}
    while queue:
        row, column, distance = queue.popleft()
        if (row, column) == (rows - 1, columns - 1):
            return distance
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == dc == 0:
                    continue
                nr, nc = row + dr, column + dc
                if 0 <= nr < rows and 0 <= nc < columns and not grid[nr][nc] and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc, distance + 1))
    return -1


def top_k_frequent(nums, k):
    buckets = [[] for _ in range(len(nums) + 1)]
    for value, frequency in Counter(nums).items():
        buckets[frequency].append(value)
    result = []
    for frequency in range(len(buckets) - 1, 0, -1):
        result.extend(buckets[frequency])
        if len(result) >= k:
            return result[:k]
    return result


def combination_sum_once(candidates, target):
    candidates.sort()
    result = []

    def search(start, remaining, path):
        if remaining == 0:
            result.append(path[:])
            return
        for index in range(start, len(candidates)):
            if index > start and candidates[index] == candidates[index - 1]:
                continue
            value = candidates[index]
            if value > remaining:
                break
            path.append(value)
            search(index + 1, remaining - value, path)
            path.pop()

    search(0, target, [])
    return result


def minimum_window(text, required):
    if not required:
        return ""
    need = Counter(required)
    have = defaultdict(int)
    formed = 0
    left = 0
    best = (float("inf"), 0, 0)
    for right, character in enumerate(text):
        have[character] += 1
        if character in need and have[character] == need[character]:
            formed += 1
        while formed == len(need):
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right + 1)
            removed = text[left]
            have[removed] -= 1
            if removed in need and have[removed] < need[removed]:
                formed -= 1
            left += 1
    return "" if best[0] == float("inf") else text[best[1]:best[2]]


def word_ladder_steps(begin, end, words):
    remaining = set(words)
    if end not in remaining:
        return 0
    queue = deque([(begin, 1)])
    while queue:
        word, steps = queue.popleft()
        if word == end:
            return steps
        for index in range(len(word)):
            for character in "abcdefghijklmnopqrstuvwxyz":
                candidate = word[:index] + character + word[index + 1:]
                if candidate in remaining:
                    remaining.remove(candidate)
                    queue.append((candidate, steps + 1))
    return 0


def max_weighted_schedule(starts, ends, profits):
    jobs = sorted(zip(starts, ends, profits), key=lambda job: job[1])
    finish_times = [job[1] for job in jobs]
    best = [0] * (len(jobs) + 1)
    for index, (start, _end, profit) in enumerate(jobs, start=1):
        compatible = bisect_left(finish_times, start + 1, 0, index - 1)
        best[index] = max(best[index - 1], profit + best[compatible])
    return best[-1]


def median_sorted_arrays(left, right):
    if len(left) > len(right):
        left, right = right, left
    total = len(left) + len(right)
    half = (total + 1) // 2
    low, high = 0, len(left)
    while low <= high:
        cut_left = (low + high) // 2
        cut_right = half - cut_left
        left_before = float("-inf") if cut_left == 0 else left[cut_left - 1]
        left_after = float("inf") if cut_left == len(left) else left[cut_left]
        right_before = float("-inf") if cut_right == 0 else right[cut_right - 1]
        right_after = float("inf") if cut_right == len(right) else right[cut_right]
        if left_before <= right_after and right_before <= left_after:
            if total % 2:
                return float(max(left_before, right_before))
            return (max(left_before, right_before) + min(left_after, right_after)) / 2
        if left_before > right_after:
            high = cut_left - 1
        else:
            low = cut_left + 1
    raise ValueError("inputs must be sorted and at least one must be non-empty")


SOLUTIONS = {
    function.__name__: function
    for function in (
        pair_sum_indices,
        valid_brackets,
        binary_search_index,
        reverse_linked_list,
        merge_sorted_linked_lists,
        max_single_trade_profit,
        normalized_palindrome,
        merge_sorted_values,
        tree_max_depth,
        longest_unique_span,
        group_anagram_words,
        three_sum_zero,
        days_until_warmer,
        rotated_array_search,
        merge_intervals,
        tree_level_order,
        is_valid_bst,
        count_islands,
        shortest_clear_path,
        top_k_frequent,
        combination_sum_once,
        minimum_window,
        word_ladder_steps,
        max_weighted_schedule,
        median_sorted_arrays,
    )
}

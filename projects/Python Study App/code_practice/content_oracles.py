from __future__ import annotations

import random
import string
from typing import Any, Callable


def pair_sum_indices(nums, target):
    for left in range(len(nums)):
        for right in range(left + 1, len(nums)):
            if nums[left] + nums[right] == target:
                return [left, right]
    return []


def binary_search_index(nums, target):
    try:
        return nums.index(target)
    except ValueError:
        return -1


def max_single_trade_profit(prices):
    return max(0, max((prices[right] - prices[left] for left in range(len(prices)) for right in range(left + 1, len(prices))), default=0))


def normalized_palindrome(text):
    normalized = "".join(character.lower() for character in text if character.isalnum())
    return normalized == normalized[::-1]


def merge_sorted_values(left, right):
    return sorted(left + right)


def longest_unique_span(text):
    best = 0
    for left in range(len(text) + 1):
        seen = set()
        for right in range(left, len(text)):
            if text[right] in seen:
                break
            seen.add(text[right])
            best = max(best, right - left + 1)
    return best


def days_until_warmer(temperatures):
    answer = []
    for index, temperature in enumerate(temperatures):
        wait = 0
        for future in range(index + 1, len(temperatures)):
            if temperatures[future] > temperature:
                wait = future - index
                break
        answer.append(wait)
    return answer


def merge_intervals(intervals):
    covered = sorted([interval[:] for interval in intervals])
    changed = True
    while changed:
        changed = False
        result = []
        for interval in covered:
            if result and interval[0] <= result[-1][1]:
                result[-1][1] = max(result[-1][1], interval[1])
                changed = True
            else:
                result.append(interval)
        covered = result
    return covered


ORACLES: dict[str, Callable[..., Any]] = {
    function.__name__: function
    for function in (
        pair_sum_indices,
        binary_search_index,
        max_single_trade_profit,
        normalized_palindrome,
        merge_sorted_values,
        longest_unique_span,
        days_until_warmer,
        merge_intervals,
    )
}


def _pair_case(rng: random.Random) -> list[Any]:
    while True:
        nums = rng.sample(range(-500, 501), rng.randint(2, 18))
        left, right = sorted(rng.sample(range(len(nums)), 2))
        target = nums[left] + nums[right]
        pairs = [(i, j) for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] + nums[j] == target]
        if pairs == [(left, right)]:
            return [nums, target]


def _binary_case(rng: random.Random) -> list[Any]:
    nums = sorted(rng.sample(range(-1000, 1001), rng.randint(0, 40)))
    target = rng.choice(nums) if nums and rng.random() < 0.6 else rng.randint(-1100, 1100)
    return [nums, target]


def _prices_case(rng: random.Random) -> list[Any]:
    return [[rng.randint(0, 200) for _ in range(rng.randint(0, 30))]]


def _palindrome_case(rng: random.Random) -> list[Any]:
    alphabet = string.ascii_letters + string.digits + " ,.!?_-"
    return ["".join(rng.choice(alphabet) for _ in range(rng.randint(0, 50)))]


def _merge_case(rng: random.Random) -> list[Any]:
    return [
        sorted(rng.randint(-50, 50) for _ in range(rng.randint(0, 20))),
        sorted(rng.randint(-50, 50) for _ in range(rng.randint(0, 20))),
    ]


def _unique_case(rng: random.Random) -> list[Any]:
    return ["".join(rng.choice("abcdef") for _ in range(rng.randint(0, 30)))]


def _temperature_case(rng: random.Random) -> list[Any]:
    return [[rng.randint(-20, 120) for _ in range(rng.randint(0, 35))]]


def _interval_case(rng: random.Random) -> list[Any]:
    intervals = []
    for _ in range(rng.randint(0, 20)):
        start = rng.randint(-30, 30)
        intervals.append([start, start + rng.randint(0, 12)])
    return [intervals]


RANDOM_CASES: dict[str, Callable[[random.Random], list[Any]]] = {
    "pair_sum_indices": _pair_case,
    "binary_search_index": _binary_case,
    "max_single_trade_profit": _prices_case,
    "normalized_palindrome": _palindrome_case,
    "merge_sorted_values": _merge_case,
    "longest_unique_span": _unique_case,
    "days_until_warmer": _temperature_case,
    "merge_intervals": _interval_case,
}


def verify_randomized(function_name: str, optimized: Callable[..., Any], count: int = 500, seed: int = 20260829) -> None:
    oracle = ORACLES[function_name]
    case_factory = RANDOM_CASES[function_name]
    rng = random.Random(seed)
    for index in range(count):
        arguments = case_factory(rng)
        actual = optimized(*[value[:] if isinstance(value, list) else value for value in arguments])
        expected = oracle(*[value[:] if isinstance(value, list) else value for value in arguments])
        assert actual == expected, f"{function_name} disagreed with its oracle on randomized case {index}: {arguments}"

from __future__ import annotations

import hashlib
import json
import math
import multiprocessing
import re
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict, deque
from heapq import heapify, heappop, heappush
from typing import Any

from .content_solutions import ListNode, TreeNode
from .schemas import ProblemDefinition, TestCase


SAFE_GLOBALS = {
    "Counter": Counter,
    "defaultdict": defaultdict,
    "deque": deque,
    "bisect_left": bisect_left,
    "bisect_right": bisect_right,
    "heapify": heapify,
    "heappop": heappop,
    "heappush": heappush,
    "ListNode": ListNode,
    "TreeNode": TreeNode,
    "__builtins__": __builtins__,
}


def content_fingerprint(problem: ProblemDefinition) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "", (problem.title + problem.statement).lower())
    signature = problem.signature.name + ":" + ",".join(item.annotation for item in problem.signature.parameters)
    return hashlib.sha256((normalized + signature).encode()).hexdigest()


def _listnode(values: list[int] | None, node_type: type = ListNode) -> Any:
    dummy = node_type()
    tail = dummy
    for value in values or []:
        tail.next = node_type(value)
        tail = tail.next
    return dummy.next


def _treenode(values: list[int | None] | None, node_type: type = TreeNode) -> Any:
    if not values or values[0] is None:
        return None
    root = node_type(values[0])
    queue = deque([root])
    index = 1
    while queue and index < len(values):
        node = queue.popleft()
        if index < len(values) and values[index] is not None:
            node.left = node_type(values[index])
            queue.append(node.left)
        index += 1
        if index < len(values) and values[index] is not None:
            node.right = node_type(values[index])
            queue.append(node.right)
        index += 1
    return root


def _serialize(value: Any, adapter: str) -> Any:
    if adapter == "listnode":
        result = []
        seen = 0
        while value and seen < 100_000:
            result.append(value.val)
            value = value.next
            seen += 1
        return result
    return value


def compare(actual: Any, expected: Any, comparator: str) -> bool:
    if comparator == "float":
        return isinstance(actual, (int, float)) and math.isclose(float(actual), float(expected), rel_tol=1e-7, abs_tol=1e-7)
    if comparator == "unordered":
        return sorted(actual) == sorted(expected) if isinstance(actual, list) else False
    if comparator == "unordered_nested":
        if not isinstance(actual, list):
            return False
        normalize = lambda rows: sorted(tuple(sorted(row)) for row in rows)
        return normalize(actual) == normalize(expected)
    return actual == expected


def run_source(source: str, problem: ProblemDefinition, test: TestCase) -> tuple[bool, str | None]:
    namespace = dict(SAFE_GLOBALS)
    try:
        exec(compile(source, f"<{problem.id}>", "exec"), namespace)
        function = namespace[problem.signature.name]
        arguments = []
        for value, parameter in zip(json.loads(json.dumps(test.arguments)), problem.signature.parameters):
            if parameter.adapter == "listnode":
                value = _listnode(value, namespace.get("ListNode", ListNode))
            elif parameter.adapter == "treenode":
                value = _treenode(value, namespace.get("TreeNode", TreeNode))
            arguments.append(value)
        actual = _serialize(function(*arguments), problem.signature.return_adapter)
        return compare(actual, test.expected, test.comparator), None
    except Exception as exc:  # validation reports the exception without hiding it
        return False, f"{type(exc).__name__}: {exc}"


def _isolated_worker(queue, source: str, problem_payload: dict[str, Any], test_payload: dict[str, Any]) -> None:
    problem = ProblemDefinition.model_validate(problem_payload)
    test = TestCase.model_validate(test_payload)
    queue.put(run_source(source, problem, test))


def run_source_isolated(
    source: str,
    problem: ProblemDefinition,
    test: TestCase,
    timeout_seconds: float = 1.5,
) -> tuple[bool, str | None]:
    context = multiprocessing.get_context("spawn")
    queue = context.Queue()
    process = context.Process(
        target=_isolated_worker,
        args=(queue, source, problem.model_dump(mode="json"), test.model_dump(mode="json")),
    )
    process.start()
    process.join(timeout_seconds)
    if process.is_alive():
        process.terminate()
        process.join(1)
        return False, "timeout"
    if process.exitcode != 0 or queue.empty():
        return False, f"validator process exited with code {process.exitcode}"
    return queue.get()


def validate_problem(problem: ProblemDefinition, existing_fingerprints: set[str] | None = None) -> dict[str, Any]:
    errors: list[str] = []
    fingerprint = content_fingerprint(problem)
    if existing_fingerprints and fingerprint in existing_fingerprints:
        errors.append("duplicate content fingerprint")
    if problem.seed_problem_id and len(set(problem.variation_dimensions)) < 2:
        errors.append("generated variants need at least two variation dimensions")
    if errors:
        return {
            "valid": False,
            "errors": errors,
            "referenceFailures": [],
            "bruteForceFailures": [],
            "wrongSolutionsRejected": [],
            "testCases": len(problem.tests),
            "explainedExamples": sum(bool(test.explanation) for test in problem.tests),
            "fingerprint": fingerprint,
        }

    reference_failures = []
    brute_force_failures = []
    runner = run_source_isolated if problem.seed_problem_id else run_source
    for test in problem.tests:
        passed, error = runner(problem.reference_solution, problem, test)
        if not passed:
            reference_failures.append({"test": test.id, "error": error or "wrong answer"})
            break
        if problem.brute_force_solution:
            brute_passed, brute_error = runner(problem.brute_force_solution, problem, test)
            if not brute_passed:
                brute_force_failures.append({"test": test.id, "error": brute_error or "wrong answer"})
                break
    if reference_failures:
        errors.append(f"reference solution failed {len(reference_failures)} tests")
    if brute_force_failures:
        errors.append(f"brute-force oracle failed {len(brute_force_failures)} tests")

    wrong_solution_results = []
    for index, source in enumerate(problem.known_wrong_solutions):
        rejected = any(not runner(source, problem, test)[0] for test in problem.tests)
        wrong_solution_results.append(rejected)
        if not rejected:
            errors.append(f"known-wrong solution {index + 1} passed every test")

    return {
        "valid": not errors,
        "errors": errors,
        "referenceFailures": reference_failures,
        "bruteForceFailures": brute_force_failures,
        "wrongSolutionsRejected": wrong_solution_results,
        "testCases": len(problem.tests),
        "explainedExamples": sum(bool(test.explanation) for test in problem.tests),
        "fingerprint": fingerprint,
    }

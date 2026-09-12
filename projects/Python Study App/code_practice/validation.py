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
from .schemas import ProblemDefinition, TestCase, analyze_integer_tree


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


def _listnode_reference(payload: Any, node_type: type = ListNode) -> tuple[Any, dict[str, Any]]:
    """Build a source list and return one selected non-tail node plus judge context."""
    if (not isinstance(payload, dict) or set(payload) != {"values", "index"}
            or not isinstance(payload["values"], list)
            or not 2 <= len(payload["values"]) <= 100_000
            or any(type(value) is not int for value in payload["values"])
            or type(payload["index"]) is not int
            or not 0 <= payload["index"] < len(payload["values"]) - 1):
        raise ValueError("List-node reference requires values plus a non-tail selected index")
    nodes = [node_type(value) for value in payload["values"]]
    for left, right in zip(nodes, nodes[1:]):
        left.next = right
    return nodes[payload["index"]], {
        "head": nodes[0],
        "nodes": nodes,
        "values": list(payload["values"]),
        "index": payload["index"],
    }


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


def _serialize(value: Any, adapter: str, strict_tree_values: bool = False) -> Any:
    if adapter == "treenode_value":
        if value is None:
            return None
        if not hasattr(value, "val"):
            raise ValueError("Returned value must be a TreeNode")
        return value.val
    if adapter in ("listnode", "listnode_ref"):
        result = []
        seen = set()
        while value is not None:
            if id(value) in seen:
                raise ValueError("Returned linked list contains a cycle")
            if len(seen) >= 100_000:
                raise ValueError("Returned linked list exceeds the supported node limit")
            seen.add(id(value))
            result.append(value.val)
            value = value.next
        return result
    if adapter == "treenode":
        result, queue, seen = [], deque([value]), set()
        while queue:
            node = queue.popleft()
            if node is None:
                result.append(None)
                continue
            if id(node) in seen:
                raise ValueError("Returned tree contains a cycle or shared child")
            if len(seen) >= 100_000:
                raise ValueError("Returned tree exceeds the supported node limit")
            if strict_tree_values and type(node.val) is not int:
                raise ValueError("Returned tree nodes must contain integer values")
            seen.add(id(node))
            result.append(node.val)
            queue.extend((node.left, node.right))
        while result and result[-1] is None:
            result.pop()
        return result
    return value


def compare(actual: Any, expected: Any, comparator: str) -> bool:
    if comparator == "balanced_bst":
        tree, goal = analyze_integer_tree(actual), analyze_integer_tree(expected)
        return (tree is not None and goal is not None and tree[1] and goal[1]
                and tree[0] == goal[0] and all(a <= b for a, b in zip(goal[0], goal[0][1:])))
    if comparator == "float":
        return isinstance(actual, (int, float)) and math.isclose(float(actual), float(expected), rel_tol=1e-7, abs_tol=1e-7)
    if comparator == "unordered":
        return sorted(actual) == sorted(expected) if isinstance(actual, list) else False
    if comparator == "unordered_nested":
        if not isinstance(actual, list):
            return False
        normalize = lambda rows: sorted(tuple(sorted(row)) for row in rows)
        return normalize(actual) == normalize(expected)
    if comparator == "unordered_rows":
        return (isinstance(actual, list) and isinstance(expected, list)
                and len(actual) == len(expected)
                and all(isinstance(row, list) and all(type(value) is int for value in row)
                        for row in actual + expected)
                and all(Counter(left) == Counter(right) for left, right in zip(actual, expected)))
    if comparator in {"wiggle", "strict_wiggle"}:
        strict = comparator == "strict_wiggle"
        return (isinstance(actual, list) and isinstance(expected, list)
                and all(type(value) is int for value in actual + expected)
                and Counter(actual) == Counter(expected)
                and all(((actual[index - 1] < actual[index]) if strict else (actual[index - 1] <= actual[index])) if index % 2
                        else ((actual[index - 1] > actual[index]) if strict else (actual[index - 1] >= actual[index]))
                        for index in range(1, len(actual))))
    return actual == expected


def _node_snapshot(value: Any, adapter: str) -> dict:
    """Retain nodes and values in list/preorder order, with bounded traversal."""
    nodes, stack = {}, [value]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        if id(node) in nodes:
            raise ValueError("Node structure contains a cycle or shared child")
        if len(nodes) >= 100_000:
            raise ValueError("Node structure exceeds the supported node limit")
        nodes[id(node)] = (node, node.val)
        if adapter == "listnode":
            stack.append(node.next)
        else:
            stack.extend((node.right, node.left))
    return nodes


def _tree_identity_snapshot(root: Any) -> dict:
    """Capture every node's value and exact child links without recursion."""
    result, stack = {}, [root]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        if id(node) in result:
            raise ValueError("Node structure contains a cycle or shared child")
        if len(result) >= 100_000:
            raise ValueError("Node structure exceeds the supported node limit")
        result[id(node)] = (node, node.val, id(node.left) if node.left is not None else None,
                            id(node.right) if node.right is not None else None)
        stack.extend((node.right, node.left))
    return result


def _tree_node_by_value(root: Any, value: Any) -> Any:
    matches, stack, seen = [], [root], set()
    while stack:
        node = stack.pop()
        if node is None:
            continue
        if id(node) in seen:
            raise ValueError("Node structure contains a cycle or shared child")
        if len(seen) >= 100_000:
            raise ValueError("Node structure exceeds the supported node limit")
        seen.add(id(node))
        if node.val == value:
            matches.append(node)
        stack.extend((node.right, node.left))
    if len(matches) != 1:
        raise ValueError("Tree-node reference value must identify exactly one source node")
    return matches[0]


def run_source(source: str, problem: ProblemDefinition, test: TestCase) -> tuple[bool, str | None]:
    namespace = dict(SAFE_GLOBALS)
    try:
        exec(compile(source, f"<{problem.id}>", "exec"), namespace)
        function = namespace[problem.signature.name]
        arguments = []
        listnode_references = {}
        for index, (value, parameter) in enumerate(zip(json.loads(json.dumps(test.arguments)), problem.signature.parameters)):
            if parameter.adapter == "listnode":
                value = _listnode(value, namespace.get("ListNode", ListNode))
            elif parameter.adapter == "listnode_ref":
                value, listnode_references[index] = _listnode_reference(
                    value, namespace.get("ListNode", ListNode)
                )
            elif parameter.adapter == "treenode":
                value = _treenode(value, namespace.get("TreeNode", TreeNode))
            elif parameter.adapter == "treenode_ref":
                value = _tree_node_by_value(arguments[parameter.source_parameter], value)
            arguments.append(value)
        original_nodes = {}
        original_tree_nodes = {}
        immutable_arguments = {
            index: json.loads(json.dumps(_serialize(arguments[index], problem.signature.parameters[index].adapter)))
            for index in problem.signature.immutable_parameters
        }
        mode = problem.signature.result_mode
        observed_adapter = (problem.signature.return_adapter if mode == "return"
                            else problem.signature.parameters[problem.signature.mutated_parameter].adapter)
        if problem.signature.node_policy == "reuse_input_nodes":
            for index, (argument, parameter) in enumerate(zip(arguments, problem.signature.parameters)):
                if parameter.adapter == observed_adapter and (mode == "return" or index == problem.signature.mutated_parameter):
                    original_nodes.update(_node_snapshot(argument, parameter.adapter))
        elif problem.signature.node_policy == "return_input_node":
            for argument, parameter in zip(arguments, problem.signature.parameters):
                if parameter.adapter == "treenode":
                    original_tree_nodes.update(_tree_identity_snapshot(argument))
        elif problem.signature.node_policy == "preserve_tree_structure":
            original_tree_nodes = _tree_identity_snapshot(arguments[problem.signature.mutated_parameter])
        output = function(*arguments)
        if mode == "return":
            actual = _serialize(output, problem.signature.return_adapter, test.comparator == "balanced_bst")
        else:
            index = problem.signature.mutated_parameter
            parameter_adapter = problem.signature.parameters[index].adapter
            changed_root = (listnode_references[index]["head"]
                            if parameter_adapter == "listnode_ref" else arguments[index])
            changed = _serialize(changed_root, parameter_adapter)
            if mode == "mutated_argument":
                actual = changed
            else:
                valid_count = type(output) is int and isinstance(changed, list) and 0 <= output <= len(changed)
                actual = {"return": output, "prefix": changed[:output] if valid_count else None}
        if problem.signature.node_policy == "reuse_input_nodes":
            observed = output if mode == "return" else arguments[problem.signature.mutated_parameter]
            returned_nodes = _node_snapshot(observed, observed_adapter)
            if set(returned_nodes) != set(original_nodes) or any(node.val != value for node, value in original_nodes.values()):
                return False, None
            if test.expected_node_order is not None:
                original_ids = list(original_nodes)
                if (len(test.expected_node_order) != len(original_ids)
                        or any(index >= len(original_ids) for index in test.expected_node_order)
                        or list(returned_nodes) != [original_ids[index] for index in test.expected_node_order]):
                    return False, None
        elif problem.signature.node_policy == "return_input_node":
            if output is not None and id(output) not in original_tree_nodes:
                return False, None
            if any(node.val != value
                   or (id(node.left) if node.left is not None else None) != left
                   or (id(node.right) if node.right is not None else None) != right
                   for node, value, left, right in original_tree_nodes.values()):
                return False, None
        elif problem.signature.node_policy == "preserve_tree_structure":
            if any(type(node.val) is not int
                   or (id(node.left) if node.left is not None else None) != left
                   or (id(node.right) if node.right is not None else None) != right
                   for node, value, left, right in original_tree_nodes.values()):
                return False, None
        elif problem.signature.node_policy == "delete_referenced_list_node":
            context = listnode_references[problem.signature.mutated_parameter]
            returned_nodes = _node_snapshot(context["head"], "listnode")
            nodes, selected = context["nodes"], context["index"]
            expected_nodes = nodes[:selected + 1] + nodes[selected + 2:]
            if list(returned_nodes) != [id(node) for node in expected_nodes]:
                return False, None
            for index, node in enumerate(nodes):
                if index == selected + 1:
                    continue
                expected_value = context["values"][selected + 1] if index == selected else context["values"][index]
                if node.val != expected_value:
                    return False, None
        if any(_serialize(arguments[index], problem.signature.parameters[index].adapter) != expected
               for index, expected in immutable_arguments.items()):
            return False, None
        return compare_result(actual, test.expected, test.comparator, mode), None
    except Exception as exc:  # validation reports the exception without hiding it
        return False, f"{type(exc).__name__}: {exc}"


def compare_result(actual: Any, expected: Any, comparator: str, mode: str = "return") -> bool:
    if mode == "returned_prefix":
        return (isinstance(actual, dict) and isinstance(expected, dict)
                and type(actual.get("return")) is int and isinstance(actual.get("prefix"), list)
                and actual["return"] == expected["return"] == len(actual["prefix"])
                and compare(actual["prefix"], expected["prefix"], comparator))
    return compare(actual, expected, comparator)


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
            "visibleTests": sum(test.visible for test in problem.tests),
            "hiddenTests": sum(not test.visible for test in problem.tests),
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
        "visibleTests": sum(test.visible for test in problem.tests),
        "hiddenTests": sum(not test.visible for test in problem.tests),
        "fingerprint": fingerprint,
    }

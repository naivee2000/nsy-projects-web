let runtimePromise;

async function runtime() {
  if (!runtimePromise) {
    importScripts("/pyodide/pyodide.js");
    runtimePromise = loadPyodide({ indexURL: "/pyodide/" });
  }
  return runtimePromise;
}

self.onmessage = async (event) => {
  if (event.data?.type === "warmup") {
    try {
      await runtime();
      self.postMessage({ type: "ready" });
    } catch (error) {
      self.postMessage({ type: "warmup_error", message: error instanceof Error ? error.message : String(error) });
    }
    return;
  }
  const started = performance.now();
  try {
    const pyodide = await runtime();
    pyodide.globals.set("job_json", JSON.stringify(event.data));
    const resultJson = await pyodide.runPythonAsync(`
import contextlib, io, json, math, traceback
from collections import Counter, defaultdict, deque
from bisect import bisect_left, bisect_right
from heapq import heappush, heappop, heapify

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def make_listnode(values, node_type=ListNode):
    dummy = node_type()
    tail = dummy
    for value in values or []:
        tail.next = node_type(value)
        tail = tail.next
    return dummy.next

def make_treenode(values, node_type=TreeNode):
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

def serialize(value, adapter, strict_tree_values=False):
    if adapter == "treenode_value":
        if value is None:
            return None
        if not hasattr(value, "val"):
            raise ValueError("Returned value must be a TreeNode")
        return value.val
    if adapter == "listnode":
        result = []
        seen = set()
        while value is not None:
            if id(value) in seen:
                raise ValueError("Returned linked list contains a cycle")
            if len(seen) >= 100000:
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
            if len(seen) >= 100000:
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

def normalize_nested(value):
    return sorted(tuple(sorted(row)) for row in value)

def node_snapshot(value, adapter):
    nodes, stack = {}, [value]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        if id(node) in nodes:
            raise ValueError("Node structure contains a cycle or shared child")
        if len(nodes) >= 100000:
            raise ValueError("Node structure exceeds the supported node limit")
        nodes[id(node)] = (node, node.val)
        if adapter == "listnode":
            stack.append(node.next)
        else:
            stack.extend((node.right, node.left))
    return nodes

def tree_identity_snapshot(root):
    result, stack = {}, [root]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        if id(node) in result:
            raise ValueError("Node structure contains a cycle or shared child")
        if len(result) >= 100000:
            raise ValueError("Node structure exceeds the supported node limit")
        result[id(node)] = (node, node.val, id(node.left) if node.left else None,
                            id(node.right) if node.right else None)
        stack.extend((node.right, node.left))
    return result

def tree_node_by_value(root, value):
    matches, stack, seen = [], [root], set()
    while stack:
        node = stack.pop()
        if node is None:
            continue
        if id(node) in seen:
            raise ValueError("Node structure contains a cycle or shared child")
        if len(seen) >= 100000:
            raise ValueError("Node structure exceeds the supported node limit")
        seen.add(id(node))
        if node.val == value:
            matches.append(node)
        stack.extend((node.right, node.left))
    if len(matches) != 1:
        raise ValueError("Tree-node reference value must identify exactly one source node")
    return matches[0]

def analyze_integer_tree(values):
    if not isinstance(values, list) or len(values) > 200001:
        return None
    if not values:
        return [], True
    if type(values[0]) is not int:
        return None
    nodes = [[values[0], -1, -1]]
    parent, index = 0, 1
    while parent < len(nodes) and index < len(values):
        for side in (1, 2):
            if index >= len(values):
                break
            value = values[index]
            index += 1
            if value is not None:
                if type(value) is not int or len(nodes) >= 100000:
                    return None
                nodes[parent][side] = len(nodes)
                nodes.append([value, -1, -1])
        parent += 1
    if index != len(values):
        return None
    heights = [0] * len(nodes)
    balanced = True
    for index in range(len(nodes) - 1, -1, -1):
        _, left, right = nodes[index]
        a, b = heights[left] if left >= 0 else 0, heights[right] if right >= 0 else 0
        balanced = balanced and abs(a - b) <= 1
        heights[index] = 1 + max(a, b)
    ordered, stack, current = [], [], 0
    while stack or current >= 0:
        while current >= 0:
            stack.append(current)
            current = nodes[current][1]
        current = stack.pop()
        ordered.append(nodes[current][0])
        current = nodes[current][2]
    return ordered, balanced

def matches(actual, expected, comparator):
    if comparator == "balanced_bst":
        tree, goal = analyze_integer_tree(actual), analyze_integer_tree(expected)
        return (tree is not None and goal is not None and tree[1] and goal[1]
                and tree[0] == goal[0] and all(a <= b for a, b in zip(goal[0], goal[0][1:])))
    if comparator == "float":
        return isinstance(actual, (int, float)) and math.isclose(float(actual), float(expected), rel_tol=1e-7, abs_tol=1e-7)
    if comparator == "unordered":
        return isinstance(actual, list) and sorted(actual) == sorted(expected)
    if comparator == "unordered_nested":
        return isinstance(actual, list) and normalize_nested(actual) == normalize_nested(expected)
    return actual == expected

def matches_result(actual, expected, comparator, mode):
    if mode == "returned_prefix":
        return (isinstance(actual, dict) and isinstance(expected, dict)
                and type(actual.get("return")) is int and isinstance(actual.get("prefix"), list)
                and actual["return"] == expected["return"] == len(actual["prefix"])
                and matches(actual["prefix"], expected["prefix"], comparator))
    return matches(actual, expected, comparator)

job = json.loads(job_json)
namespace = dict(globals())
console_output = io.StringIO()
try:
    with contextlib.redirect_stdout(console_output), contextlib.redirect_stderr(console_output):
        compiled = compile(job["source"], "<submission>", "exec")
        exec(compiled, namespace)
    function = namespace.get(job["signature"]["name"])
    if not callable(function):
        raise NameError(f'Expected a function named {job["signature"]["name"]}')
except SyntaxError as error:
    result_payload = {"status": "syntax_error", "message": f"{error.msg} (line {error.lineno})", "cases": [], "stdout": console_output.getvalue()}
except Exception as error:
    result_payload = {"status": "runtime_error", "message": f"{type(error).__name__}: {error}", "cases": [], "stdout": console_output.getvalue()}
else:
    cases = []
    status = "accepted"
    message = "All tests passed."
    for test in job["tests"]:
        try:
            arguments = []
            for value, parameter in zip(json.loads(json.dumps(test["arguments"])), job["signature"]["parameters"]):
                if parameter.get("adapter") == "listnode":
                    value = make_listnode(value, namespace.get("ListNode", ListNode))
                elif parameter.get("adapter") == "treenode":
                    value = make_treenode(value, namespace.get("TreeNode", TreeNode))
                elif parameter.get("adapter") == "treenode_ref":
                    value = tree_node_by_value(arguments[parameter["source_parameter"]], value)
                arguments.append(value)
            original_nodes = {}
            original_tree_nodes = {}
            mode = job["signature"].get("result_mode", "return")
            observed_adapter = (job["signature"].get("return_adapter", "raw") if mode == "return"
                                else job["signature"]["parameters"][job["signature"]["mutated_parameter"]].get("adapter", "raw"))
            if job["signature"].get("node_policy") == "reuse_input_nodes":
                for index, (argument, parameter) in enumerate(zip(arguments, job["signature"]["parameters"])):
                    if parameter.get("adapter") == observed_adapter and (mode == "return" or index == job["signature"]["mutated_parameter"]):
                        original_nodes.update(node_snapshot(argument, parameter["adapter"]))
            elif job["signature"].get("node_policy") == "return_input_node":
                for argument, parameter in zip(arguments, job["signature"]["parameters"]):
                    if parameter.get("adapter") == "treenode":
                        original_tree_nodes.update(tree_identity_snapshot(argument))
            with contextlib.redirect_stdout(console_output), contextlib.redirect_stderr(console_output):
                output = function(*arguments)
                mode = job["signature"].get("result_mode", "return")
                if mode == "return":
                    actual = serialize(output, job["signature"].get("return_adapter", "raw"), test.get("comparator") == "balanced_bst")
                else:
                    index = job["signature"]["mutated_parameter"]
                    changed = serialize(arguments[index], job["signature"]["parameters"][index].get("adapter", "raw"))
                    if mode == "mutated_argument":
                        actual = changed
                    else:
                        valid_count = type(output) is int and isinstance(changed, list) and 0 <= output <= len(changed)
                        actual = {"return": output, "prefix": changed[:output] if valid_count else None}
            passed = matches_result(actual, test["expected"], test.get("comparator", "exact"), mode)
            contract_error = None
            if test.get("comparator") == "balanced_bst" and not passed:
                contract_error = "Return a height-balanced BST containing every input value exactly once in inorder. The example shape is only one valid output."
            if mode == "returned_prefix" and not valid_count:
                contract_error = "Return an integer k between zero and the updated list length; nums[:k] is checked."
            if job["signature"].get("node_policy") == "reuse_input_nodes":
                observed = output if mode == "return" else arguments[job["signature"]["mutated_parameter"]]
                returned_nodes = node_snapshot(observed, observed_adapter)
                if set(returned_nodes) != set(original_nodes) or any(node.val != value for node, value in original_nodes.values()):
                    passed = False
                    contract_error = "Reconnect every original node exactly once without changing its value."
                order = test.get("expected_node_order")
                if order is not None:
                    original_ids = list(original_nodes)
                    if (len(order) != len(original_ids) or any(type(index) is not int or index < 0 or index >= len(original_ids) for index in order)
                            or list(returned_nodes) != [original_ids[index] for index in order]):
                        passed = False
                        contract_error = "Reconnect the original nodes in the required order, including nodes with equal values."
            elif job["signature"].get("node_policy") == "return_input_node":
                if output is None or id(output) not in original_tree_nodes:
                    passed = False
                    contract_error = "Return the required existing node from the input tree without changing the tree."
                elif any(node.val != value
                         or (id(node.left) if node.left else None) != left
                         or (id(node.right) if node.right else None) != right
                         for node, value, left, right in original_tree_nodes.values()):
                    passed = False
                    contract_error = "Return the required existing node from the input tree without changing the tree."
            cases.append({"id": test["id"], "passed": passed, "actual": actual, "expected": test["expected"], "visible": test.get("visible", False), "arguments": test["arguments"] if test.get("visible", False) or not passed else None})
            if contract_error:
                cases[-1]["error"] = contract_error
            if not passed:
                status = "wrong_answer"
                message = "A test produced an unexpected result."
                if job.get("stopOnFailure", False):
                    break
        except Exception as error:
            status = "runtime_error"
            message = f"{type(error).__name__}: {error}"
            cases.append({"id": test["id"], "passed": False, "error": message, "expected": test["expected"], "visible": test.get("visible", False), "arguments": test["arguments"]})
            if job.get("stopOnFailure", False):
                break
    result_payload = {"status": status, "message": message, "cases": cases, "stdout": console_output.getvalue()}
json.dumps(result_payload)
`);
    const result = JSON.parse(resultJson);
    result.runtimeMs = performance.now() - started;
    self.postMessage(result);
  } catch (error) {
    self.postMessage({
      status: "runtime_error",
      message: error instanceof Error ? error.message : String(error),
      cases: [],
      runtimeMs: performance.now() - started,
    });
  }
};

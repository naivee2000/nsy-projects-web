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

def make_listnode(values):
    dummy = ListNode()
    tail = dummy
    for value in values or []:
        tail.next = ListNode(value)
        tail = tail.next
    return dummy.next

def make_treenode(values):
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    index = 1
    while queue and index < len(values):
        node = queue.popleft()
        if index < len(values) and values[index] is not None:
            node.left = TreeNode(values[index])
            queue.append(node.left)
        index += 1
        if index < len(values) and values[index] is not None:
            node.right = TreeNode(values[index])
            queue.append(node.right)
        index += 1
    return root

def serialize(value, adapter):
    if adapter == "listnode":
        result = []
        seen = 0
        while value is not None and seen < 100000:
            result.append(value.val)
            value = value.next
            seen += 1
        return result
    return value

def normalize_nested(value):
    return sorted(tuple(sorted(row)) for row in value)

def matches(actual, expected, comparator):
    if comparator == "float":
        return isinstance(actual, (int, float)) and math.isclose(float(actual), float(expected), rel_tol=1e-7, abs_tol=1e-7)
    if comparator == "unordered":
        return isinstance(actual, list) and sorted(actual) == sorted(expected)
    if comparator == "unordered_nested":
        return isinstance(actual, list) and normalize_nested(actual) == normalize_nested(expected)
    return actual == expected

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
            for value, parameter in zip(test["arguments"], job["signature"]["parameters"]):
                if parameter.get("adapter") == "listnode":
                    value = make_listnode(value)
                elif parameter.get("adapter") == "treenode":
                    value = make_treenode(value)
                arguments.append(value)
            with contextlib.redirect_stdout(console_output), contextlib.redirect_stderr(console_output):
                actual = serialize(function(*arguments), job["signature"].get("return_adapter", "raw"))
            passed = matches(actual, test["expected"], test.get("comparator", "exact"))
            cases.append({"id": test["id"], "passed": passed, "actual": actual, "expected": test["expected"], "visible": test.get("visible", False), "arguments": test["arguments"] if test.get("visible", False) else None})
            if not passed:
                status = "wrong_answer"
                message = "A test produced an unexpected result."
                if job.get("stopOnFailure", False):
                    break
        except Exception as error:
            status = "runtime_error"
            message = f"{type(error).__name__}: {error}"
            cases.append({"id": test["id"], "passed": False, "error": message, "expected": test["expected"], "visible": test.get("visible", False), "arguments": test["arguments"] if test.get("visible", False) else None})
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

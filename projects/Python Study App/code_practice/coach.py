from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any

from .schemas import ProblemDefinition


@dataclass(frozen=True)
class CoachReply:
    step: int
    max_steps: int
    title: str
    observation: str
    nudge: str
    question: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "maxSteps": self.max_steps,
            "title": self.title,
            "observation": self.observation,
            "nudge": self.nudge,
            "question": self.question,
            "canContinue": self.step < self.max_steps,
            "source": "offline-static-coach",
        }


def _function_node(tree: ast.AST, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def _off_by_one_ranges(function: ast.AST) -> list[int]:
    lines: list[int] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != "range":
            continue
        if not node.args:
            continue
        stop = node.args[-1]
        if (
            isinstance(stop, ast.BinOp)
            and isinstance(stop.op, ast.Sub)
            and isinstance(stop.right, ast.Constant)
            and stop.right.value == 1
            and isinstance(stop.left, ast.Call)
            and isinstance(stop.left.func, ast.Name)
            and stop.left.func.id == "len"
        ):
            lines.append(node.lineno)
    return lines


def _code_observation(source_code: str, problem: ProblemDefinition) -> str:
    try:
        tree = ast.parse(source_code)
    except SyntaxError as error:
        return f"Python cannot finish reading line {error.lineno}: {error.msg}."

    function = _function_node(tree, problem.signature.name)
    if function is None:
        return f"The judge cannot find the required `{problem.signature.name}` function."
    off_by_one = _off_by_one_ranges(function)
    if off_by_one:
        rendered = ", ".join(str(line) for line in off_by_one)
        return (
            f"The range ending on line {rendered} subtracts 1 from `len(...)`. Because Python's range already "
            "excludes its stop value, the final position is never visited."
        )
    if any(isinstance(node, ast.Pass) for node in ast.walk(function)):
        return "The function still contains `pass`; make sure every intended path reaches a meaningful return."
    returns = [node for node in ast.walk(function) if isinstance(node, ast.Return)]
    if not returns:
        return "The function has no return statement, so Python returns `None` automatically."
    if any(isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True for node in ast.walk(function)):
        return "A `while True` loop has no statically visible stopping condition; trace how control leaves that loop."
    nested_loops = sum(isinstance(node, (ast.For, ast.While)) for node in ast.walk(function))
    if nested_loops >= 2 and problem.target_time_complexity in {"O(n)", "O(log n)", "O(1)"}:
        return (
            f"The function contains {nested_loops} loops while the target is {problem.target_time_complexity}. "
            "Correctness comes first, but this structure may also revisit work unnecessarily."
        )
    return "The function is syntactically complete, so the next useful move is to trace the first mismatching example."


def _case_observation(cases: list[dict[str, Any]]) -> str:
    failed = next((case for case in cases if not case.get("passed")), None)
    if failed:
        actual = failed.get("error") or failed.get("actual")
        expected = failed.get("expected")
        arguments = failed.get("arguments")
        input_note = f" For input {arguments!r}," if arguments is not None else ""
        return f"{input_note} the expected result is {expected!r}, but the function currently produces {actual!r}."
    passed = sum(bool(case.get("passed")) for case in cases)
    if cases:
        return f"The submission passes {passed} of {len(cases)} reported tests."
    return "The run stopped before it could produce a comparable result."


def build_coaching(
    problem: ProblemDefinition,
    source_code: str,
    status: str,
    message: str,
    cases: list[dict[str, Any]],
    step: int,
) -> CoachReply:
    """Create one progressive, non-solution coaching step without executing source_code."""
    step = max(1, min(3, step))
    case_note = _case_observation(cases)
    code_note = _code_observation(source_code, problem)

    if status == "syntax_error":
        steps = (
            ("Make Python readable first", message, code_note, "What is the smallest indentation or punctuation change that lets the function run?"),
            ("Check the function boundary", case_note, "Confirm every line belonging to the function is indented consistently.", "Does `return` line up with the statements that should run before it?"),
            ("Run one tiny example", case_note, "After syntax is fixed, run the first example before changing the algorithm.", "What value should each variable hold immediately before `return`?"),
        )
    elif status == "runtime_error":
        steps = (
            ("Locate the first crash", message, "Read the exception type and line before changing the algorithm.", "Which value on that line has a different type or shape than you assumed?"),
            ("Trace the crashing input", case_note, code_note, "What is the last variable value you know is valid before the exception?"),
            ("Guard one assumption", case_note, problem.hints[0], "Which empty, missing, or boundary condition needs an explicit check?"),
        )
    elif status == "timeout":
        steps = (
            ("Find the stalled progress", message, code_note, "Which loop variable or data structure must change on every iteration?"),
            ("Prove termination", case_note, "Write down the quantity that strictly moves toward the stopping condition.", "Can that quantity ever stay unchanged on a branch?"),
            ("Remove repeated work", case_note, problem.hints[0], "Which result or visited state could be remembered instead of recomputed?"),
        )
    else:
        steps = (
            ("Compare one concrete mismatch", case_note, "Do not rewrite everything yet. Identify the first point where your trace diverges from the expected output.", "Which index, character, node, or state is missing from the current result?"),
            ("Inspect the control flow", case_note, code_note, "If you trace only the failing example, which branch prevents the missing value from being processed?"),
            ("Aim at the right invariant", case_note, problem.hints[0], "What fact should remain true after each loop iteration or recursive call?"),
        )

    title, observation, nudge, question = steps[step - 1]
    return CoachReply(step, 3, title, observation, nudge, question)

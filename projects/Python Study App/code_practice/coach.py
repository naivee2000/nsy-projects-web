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
    nudge: str = ""
    question: str = ""
    diagnostic: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {"step": 1, "maxSteps": 1, "title": self.title,
                "observation": self.observation, "nudge": self.nudge, "question": "",
                "canContinue": False, "source": "offline-static-coach", "diagnostic": self.diagnostic}


def _location(source: str, diagnostic: dict[str, Any]) -> dict[str, Any]:
    result = dict(diagnostic)
    lines = source.splitlines()
    line = result.get("line")
    if type(line) is int and 1 <= line <= len(lines):
        result["sourceExcerpt"] = lines[line - 1][:300]
    else:
        result.update(line=None, column=None, sourceExcerpt=None)
    return result


def build_coaching(problem: ProblemDefinition, source_code: str, status: str, message: str,
                   cases: list[dict[str, Any]], step: int = 1, *, mode: str = "debug",
                   diagnostic: dict[str, Any] | None = None) -> CoachReply:
    """Explain observed errors without executing code or inferring algorithms.

    Legacy step/mode arguments remain compatible; offline replies always diagnose.
    """
    tree = None
    try:
        tree = ast.parse(source_code)
    except SyntaxError as error:
        diagnostic = {"exceptionType": type(error).__name__, "message": error.msg,
                      "line": error.lineno, "column": error.offset}
        status = "syntax_error"
    diagnostic = diagnostic or next((case.get("diagnostic") for case in cases if case.get("diagnostic")), None)
    detail = _location(source_code, diagnostic) if diagnostic else None
    error_type = (detail or {}).get("exceptionType") or message.split(":", 1)[0]
    description = (detail or {}).get("message") or message
    line = (detail or {}).get("sourceExcerpt") or ""
    if status == "syntax_error":
        correction = "Check the punctuation at the reported location."
        if error_type in {"IndentationError", "TabError"} or "indent" in description.lower():
            correction = "Use consistent indentation for this block; avoid mixing tabs and spaces."
        elif line.rstrip().endswith(";"):
            # Verify the one-character repair before suggesting it.
            lines = source_code.splitlines()
            number = (detail or {}).get("line")
            if number:
                lines[number-1] = lines[number-1].rstrip()[:-1] + ":"
                try:
                    ast.parse("\n".join(lines))
                    correction = "Replace the final semicolon on this statement header with a colon (:)."
                except SyntaxError:
                    pass
        elif "never closed" in description:
            correction = "Close the bracket or parenthesis opened at the reported location."
        elif "unterminated string" in description:
            correction = "Close the string with a matching quote."
        elif "expected ':'" in description:
            correction = "Add a colon (:) at the end of this statement header."
        return CoachReply(1, 1, "Python could not read this code", description, correction, diagnostic=detail)
    if status == "timeout":
        suspected = None
        if tree:
            # Deliberately narrow: other loops can terminate through calls or
            # mutations. Loop count alone says nothing about correctness.
            suspected = next((node for node in ast.walk(tree) if isinstance(node, ast.While)
                              and isinstance(node.test, ast.Constant) and node.test.value is True
                              and all(isinstance(stmt, (ast.Pass, ast.Continue)) for stmt in node.body)), None)
        if suspected:
            detail = _location(source_code, {"exceptionType": "Timeout", "message": message,
                                            "line": suspected.lineno, "column": suspected.col_offset + 1})
        return CoachReply(1, 1, "Execution timed out", message,
                          "Possible cause: this unconditional loop has no operation that exits it." if suspected else
                          "The cause is uncertain: a loop may not terminate, or the computation may take too long.", diagnostic=detail)
    if status == "runtime_error":
        explanations = {
            "IndexError": "An index is outside the available positions. Check the index and collection length on this line.",
            "NameError": "This name is not defined. Check its spelling and whether it was assigned before this line.",
            "UnboundLocalError": "This local variable is used before it has a value on this execution path.",
            "TypeError": "This operation received an incompatible value or arguments. Check the types named in the error.",
            "AttributeError": "This value does not provide the named attribute or method. Check its spelling and the value's type.",
            "RecursionError": "Python's recursion depth limit was exceeded. Possible causes include a missing stopping condition, unchanged recursive arguments, or legitimately deep input.",
            "KeyError": "The requested dictionary key is missing.",
            "ZeroDivisionError": "The divisor became zero on this execution path.",
        }
        return CoachReply(1, 1, "Maximum recursion depth reached" if error_type == "RecursionError" else "Python stopped with an error",
                          f"{error_type}: {description}" if detail else description,
                          explanations.get(error_type, "Inspect the reported exception and location."), diagnostic=detail)
    return CoachReply(1, 1, "Output comparison", "Your code ran; the output differs from the expected answer."
                      if status != "accepted" else "Your code ran successfully.")

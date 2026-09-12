from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Comparator = Literal["exact", "float", "unordered", "unordered_nested", "balanced_bst", "wiggle", "strict_wiggle"]
ParameterAdapter = Literal["raw", "listnode", "listnode_ref", "treenode", "treenode_ref"]
ReturnAdapter = Literal["raw", "listnode", "treenode", "treenode_value"]
AttemptResult = Literal["accepted", "wrong_answer", "syntax_error", "runtime_error", "timeout"]


def analyze_integer_tree(values: Any) -> tuple[list[int], bool] | None:
    """Read compact level-order JSON without recursion; reject malformed trees.

    Return the inorder values and whether EVERY subtree is height-balanced.
    This deliberately does not choose a canonical root or output shape.
    """
    if not isinstance(values, list) or len(values) > 200_001:
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
                if type(value) is not int or len(nodes) >= 100_000:
                    return None
                nodes[parent][side] = len(nodes)
                nodes.append([value, -1, -1])
        parent += 1
    if index != len(values):
        return None  # Disconnected values after the last reachable child slot.
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


class ParameterDefinition(BaseModel):
    name: str
    annotation: str
    adapter: ParameterAdapter = "raw"
    # A treenode_ref is selected by its unique value from this earlier
    # treenode parameter. A listnode_ref carries its source list and selected
    # index inside the argument payload, so it does not use this field.
    source_parameter: int | None = Field(default=None, ge=0)


class FunctionSignature(BaseModel):
    name: str
    parameters: list[ParameterDefinition]
    returns: str
    return_adapter: ReturnAdapter = "raw"
    node_policy: Literal[
        "values", "reuse_input_nodes", "return_input_node", "delete_referenced_list_node"
    ] = "values"
    result_mode: Literal["return", "mutated_argument", "returned_prefix"] = "return"
    mutated_parameter: int | None = Field(default=None, ge=0)
    immutable_parameters: list[Annotated[int, Field(strict=True, ge=0)]] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_node_policy(self) -> "FunctionSignature":
        if (len(set(self.immutable_parameters)) != len(self.immutable_parameters)
                or any(index >= len(self.parameters) for index in self.immutable_parameters)):
            raise ValueError("Immutable parameter indices must be unique and in range")
        for index, parameter in enumerate(self.parameters):
            if parameter.adapter == "treenode_ref":
                if (parameter.source_parameter is None or parameter.source_parameter >= index
                        or self.parameters[parameter.source_parameter].adapter != "treenode"):
                    raise ValueError("Tree-node references require an earlier TreeNode source parameter")
            elif parameter.adapter == "listnode_ref":
                if parameter.source_parameter is not None:
                    raise ValueError("List-node reference payloads cannot select a separate source parameter")
            elif parameter.source_parameter is not None:
                raise ValueError("Only tree-node references may select a source parameter")
        if self.result_mode == "return":
            if self.mutated_parameter is not None:
                raise ValueError("Return-value mode cannot select a mutated parameter")
        elif self.mutated_parameter is None or self.mutated_parameter >= len(self.parameters):
            raise ValueError("Mutation mode requires a valid parameter index")
        elif self.mutated_parameter in self.immutable_parameters:
            raise ValueError("A selected mutation parameter cannot also be immutable")
        elif self.result_mode == "returned_prefix" and (
            self.parameters[self.mutated_parameter].adapter != "raw"
            or not self.parameters[self.mutated_parameter].annotation.startswith("list[")
            or self.returns != "int"
        ):
            raise ValueError("Returned-prefix mode requires an integer count and a raw list parameter")
        if self.node_policy == "reuse_input_nodes":
            adapter = (self.return_adapter if self.result_mode == "return"
                       else self.parameters[self.mutated_parameter].adapter)
            if (self.result_mode == "returned_prefix" or adapter not in ("listnode", "treenode")
                    or not any(p.adapter == adapter for p in self.parameters)):
                raise ValueError("Node reuse requires matching linked-list or tree inputs and observed output")
        elif self.node_policy == "return_input_node":
            if (self.result_mode != "return" or self.return_adapter != "treenode_value"
                    or not any(parameter.adapter == "treenode" for parameter in self.parameters)):
                raise ValueError("Returned-node identity requires a TreeNode input and TreeNode value output")
        elif self.node_policy == "delete_referenced_list_node":
            if (self.result_mode != "mutated_argument" or self.mutated_parameter is None
                    or self.parameters[self.mutated_parameter].adapter != "listnode_ref"
                    or self.returns != "None" or self.return_adapter != "raw"):
                raise ValueError("Referenced-node deletion requires a mutated ListNode reference and no return value")
        elif self.return_adapter == "treenode_value":
            raise ValueError("TreeNode value output requires returned-node identity checking")
        if any(self.parameters[index].adapter in ("listnode_ref", "treenode_ref")
               for index in self.immutable_parameters):
            raise ValueError("Reference parameters cannot be selected for standalone immutability checks")
        return self


class TestCase(BaseModel):
    id: str
    arguments: list[Any]
    expected: Any
    comparator: Comparator = "exact"
    visible: bool = False
    explanation: str | None = None
    # Indices into original nodes: parameter order, then list/preorder traversal.
    # Mutation contracts index only the selected argument. None leaves equal-
    # valued nodes interchangeable when the source contract permits that.
    expected_node_order: list[Annotated[int, Field(strict=True, ge=0)]] | None = None

    @model_validator(mode="after")
    def validate_node_order(self) -> "TestCase":
        if self.expected_node_order is not None and len(set(self.expected_node_order)) != len(self.expected_node_order):
            raise ValueError("Expected node order cannot repeat a node index")
        return self


class DifficultyRubric(BaseModel):
    algorithmic_insight: int = Field(ge=0, le=3)
    prerequisites: int = Field(ge=0, le=2)
    implementation: int = Field(ge=0, le=2)
    performance_pressure: int = Field(ge=0, le=2)
    edge_cases: int = Field(ge=0, le=1)

    @property
    def total(self) -> int:
        return max(1, sum(self.model_dump().values()))


class ProblemDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    version: int = 1
    status: Literal["draft", "validating", "rejected", "approved"] = "approved"
    title: str
    summary: str
    statement: str
    constraints: list[str]
    topics: list[str]
    prerequisites: list[str] = []
    signature: FunctionSignature
    starter_code: str
    reference_solution: str
    brute_force_solution: str | None = None
    known_wrong_solutions: list[str]
    target_time_complexity: str
    target_space_complexity: str
    estimated_minutes: int = Field(ge=5, le=180)
    rubric: DifficultyRubric
    hints: list[str]
    editorial: str
    tests: list[TestCase]
    variation_dimensions: list[str] = []
    seed_problem_id: str | None = None
    prompt_version: str | None = None

    @property
    def difficulty(self) -> int:
        return self.rubric.total

    @model_validator(mode="after")
    def validate_learning_content(self) -> "ProblemDefinition":
        for test in self.tests:
            for index, parameter in enumerate(self.signature.parameters):
                if parameter.adapter != "listnode_ref":
                    continue
                value = test.arguments[index] if index < len(test.arguments) else None
                if (not isinstance(value, dict) or set(value) != {"values", "index"}
                        or not isinstance(value["values"], list)
                        or not 2 <= len(value["values"]) <= 100_000
                        or any(type(item) is not int for item in value["values"])
                        or type(value["index"]) is not int
                        or not 0 <= value["index"] < len(value["values"]) - 1):
                    raise ValueError("List-node references require values plus a non-tail selected index")
                if (self.signature.node_policy == "delete_referenced_list_node"
                        and (not isinstance(test.expected, list)
                             or len(test.expected) != len(value["values"]) - 1)):
                    raise ValueError("Referenced-node deletion must expect the full list with one node removed")
        if any(t.comparator == "balanced_bst" for t in self.tests):
            if (self.signature.result_mode != "return" or self.signature.return_adapter != "treenode"
                    or len(self.signature.parameters) != 1
                    or self.signature.parameters[0].adapter not in ("raw", "listnode")
                    or any(t.comparator != "balanced_bst" for t in self.tests)):
                raise ValueError("Balanced-BST judging requires one sorted sequence input, a returned tree, and consistent comparators")
            for test in self.tests:
                if (len(test.arguments) != 1 or not isinstance(test.arguments[0], list)
                        or any(type(value) is not int for value in test.arguments[0])):
                    raise ValueError("Balanced-BST input must be a sorted integer sequence")
                values = test.arguments[0]
                expected = analyze_integer_tree(test.expected)
                if (any(a > b for a, b in zip(values, values[1:]))
                        or expected is None or not expected[1] or expected[0] != values):
                    raise ValueError("Balanced-BST expectation must be balanced and preserve the entire sorted input inorder")
        wiggle_modes = {t.comparator for t in self.tests} & {"wiggle", "strict_wiggle"}
        if wiggle_modes:
            mutated = self.signature.mutated_parameter
            if (self.signature.result_mode != "mutated_argument" or mutated is None
                    or len(wiggle_modes) != 1
                    or self.signature.parameters[mutated].adapter != "raw"
                    or not self.signature.parameters[mutated].annotation.startswith("list[")
                    or any(t.comparator not in wiggle_modes for t in self.tests)):
                raise ValueError("Wiggle judging requires one consistently compared mutated raw list")
            strict = "strict_wiggle" in wiggle_modes
            for test in self.tests:
                original = test.arguments[mutated] if len(test.arguments) > mutated else None
                expected = test.expected
                if (not isinstance(original, list) or not isinstance(expected, list)
                        or any(type(value) is not int for value in original + expected)
                        or Counter(original) != Counter(expected)
                        or any(not ((a < b if strict else a <= b) if index % 2
                                    else (a > b if strict else a >= b))
                               for index, (a, b) in enumerate(zip(expected, expected[1:]), 1))):
                    raise ValueError("Wiggle expectations must be valid integer permutations with the declared inequalities")
        if self.signature.node_policy != "reuse_input_nodes" and any(t.expected_node_order is not None for t in self.tests):
            raise ValueError("Expected node order requires the node-reuse policy")
        if self.signature.result_mode == "returned_prefix":
            for test in self.tests:
                expected = test.expected
                if (not isinstance(expected, dict) or set(expected) != {"return", "prefix"}
                        or type(expected["return"]) is not int or not isinstance(expected["prefix"], list)
                        or expected["return"] != len(expected["prefix"])):
                    raise ValueError("Prefix expectations need an integer return equal to the prefix length")
        visible = sum(test.visible for test in self.tests)
        hidden = len(self.tests) - visible
        if visible < 2:
            raise ValueError("a problem needs at least two visible examples")
        if hidden < 12:
            raise ValueError("a problem needs at least twelve hidden tests")
        if len(self.hints) != 4:
            raise ValueError("hints must contain concept, strategy, pseudocode, and editorial levels")
        if len(self.known_wrong_solutions) < 2:
            raise ValueError("at least two known-wrong solutions are required")
        return self


class AttemptCreate(BaseModel):
    problem_id: str
    problem_version: int
    source_code: str
    result: AttemptResult
    runtime_ms: float = Field(ge=0)
    tests_passed: int = Field(ge=0)
    tests_total: int = Field(ge=0)
    elapsed_study_seconds: int = Field(default=0, ge=0)
    hint_level: int = Field(default=0, ge=0, le=4)


class Attempt(AttemptCreate):
    id: int
    created_at: datetime


class ReviewState(BaseModel):
    problem_id: str
    interval_index: int
    due_at: datetime
    latest_result: AttemptResult
    latest_accepted_source: str | None = None


class VariantDraft(BaseModel):
    problem: ProblemDefinition
    variation_dimensions: list[Literal["data_model", "operation", "output_shape", "constraints", "algorithm_combination"]]
    generation_notes: str

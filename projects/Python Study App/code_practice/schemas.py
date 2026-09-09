from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Comparator = Literal["exact", "float", "unordered", "unordered_nested"]
Adapter = Literal["raw", "listnode", "treenode"]
AttemptResult = Literal["accepted", "wrong_answer", "syntax_error", "runtime_error", "timeout"]


class ParameterDefinition(BaseModel):
    name: str
    annotation: str
    adapter: Adapter = "raw"


class FunctionSignature(BaseModel):
    name: str
    parameters: list[ParameterDefinition]
    returns: str
    return_adapter: Adapter = "raw"


class TestCase(BaseModel):
    id: str
    arguments: list[Any]
    expected: Any
    comparator: Comparator = "exact"
    visible: bool = False
    explanation: str | None = None


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

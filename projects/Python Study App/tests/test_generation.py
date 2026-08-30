from fastapi.testclient import TestClient

from code_practice.app import app
from code_practice.catalog import refresh_catalog
from code_practice.content import PROBLEMS
from code_practice.database import list_variants, save_variant, update_variant_status
from code_practice.generate import validate_variant


def generated_copy(problem_id: str):
    problem = PROBLEMS[0].model_copy(deep=True)
    problem.id = problem_id
    problem.title = "Warehouse Pair Audit"
    problem.summary = "Find two warehouse adjustments that reconcile a requested balance."
    problem.statement = "Return two distinct positions whose signed warehouse adjustments total the requested balance."
    problem.status = "draft"
    problem.seed_problem_id = PROBLEMS[0].id
    problem.prompt_version = "test-v1"
    problem.variation_dimensions = ["data_model", "operation"]
    return problem


def test_valid_variant_requires_validation_and_explicit_approval():
    variant = generated_copy("warehouse-pair-audit")
    save_variant(variant.model_dump(mode="json"), variant.seed_problem_id or "")
    refresh_catalog()
    with TestClient(app) as client:
        assert variant.id not in {item["id"] for item in client.get("/api/problems").json()}

    report = validate_variant(variant.id)
    assert report["valid"]
    row = next(item for item in list_variants() if item["problem_id"] == variant.id)
    assert row["status"] == "validating"

    assert update_variant_status(variant.id, "approved", report)
    refresh_catalog()
    with TestClient(app) as client:
        assert variant.id in {item["id"] for item in client.get("/api/problems").json()}


def test_infinite_reference_is_rejected_by_validation_timeout():
    variant = generated_copy("nonterminating-pair-audit")
    variant.title = "Nonterminating Pair Audit"
    variant.statement += " This intentionally malformed draft verifies the validator timeout."
    variant.reference_solution = "def pair_sum_indices(nums, target):\n    while True:\n        pass\n"
    save_variant(variant.model_dump(mode="json"), variant.seed_problem_id or "")
    report = validate_variant(variant.id)
    assert not report["valid"]
    assert report["referenceFailures"][0]["error"] == "timeout"
    row = next(item for item in list_variants() if item["problem_id"] == variant.id)
    assert row["status"] == "rejected"

#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from car_compare.parser import parse_vehicle_query  # noqa: E402
from car_compare.vehicle_match import vehicle_text_match_score  # noqa: E402


def main() -> int:
    fixture_path = ROOT / "tests" / "fixtures" / "search_accuracy_benchmark.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    total = 0
    correct = 0
    false_positives = 0
    false_negatives = 0
    samples: list[dict[str, object]] = []
    for sample in fixture["samples"]:
        request = parse_vehicle_query(sample["query"])
        sample_correct = 0
        failures = []
        for expected, title in sample["cases"]:
            actual = bool(
                vehicle_text_match_score(request, title, "", "autotrader_browser")["accepted"]
            )
            total += 1
            if actual == expected:
                correct += 1
                sample_correct += 1
            else:
                false_negatives += int(bool(expected))
                false_positives += int(not expected)
                failures.append({"expected": expected, "actual": actual, "title": title})
        samples.append(
            {
                "query": sample["query"],
                "correct": sample_correct,
                "total": len(sample["cases"]),
                "failures": failures,
            }
        )
    accuracy = correct / total if total else 0.0
    baseline = float(fixture["baseline"]["accuracy"])
    result = {
        "correct": correct,
        "total": total,
        "accuracy": round(accuracy, 4),
        "baselineAccuracy": baseline,
        "relativeImprovement": round((accuracy / baseline) - 1, 4) if baseline else None,
        "falsePositives": false_positives,
        "falseNegatives": false_negatives,
        "targetAccuracy": fixture["baseline"]["target_accuracy"],
        "samples": samples,
    }
    print(json.dumps(result, indent=2))
    return 0 if accuracy >= float(fixture["baseline"]["target_accuracy"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())

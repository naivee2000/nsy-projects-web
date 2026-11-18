"""Fast authoring preflight using the same harness as the browser; the release report requires Chrome."""

import json
from pathlib import Path
import sys

from code_practice.database_catalog import CATALOG, pandas_starter, public_case
from code_practice.database_judge import matches


def main():
    worker = Path("frontend/public/database-worker.js").read_text()
    code = worker.split("const harness = `\n", 1)[1].split("\n`;", 1)[0]
    scope = {}
    exec(code, scope)
    count = 0
    for key in map(int, sys.argv[1:]) if len(sys.argv) > 1 else sorted(CATALOG):
        p = CATALOG[key]
        inputs = [public_case(p, c) for c in p["cases"]]
        for idx, body in enumerate([p["pandas"], *p["wrong_pandas"]]):
            outcomes = json.loads(
                scope["judge"](
                    pandas_starter(p, body=body), p["schema"], p["runner"], inputs, p["result_table"]
                )
            )
            errors = [(i, o.get("error")) for i, o in enumerate(outcomes, 1) if o.get("error")]
            mismatches = [
                i
                for i, (c, o) in enumerate(zip(inputs, outcomes), 1)
                if "actual" in o
                and not matches(
                    c["expected"],
                    o["actual"]["columns"],
                    o["actual"]["rows"],
                    ordered=p["ordered"],
                    date_columns=p["date_columns"],
                )
            ]
            if (idx == 0 and (errors or mismatches)) or (idx and not mismatches):
                print(key, idx, "errors", errors[:1], "mismatches", mismatches[:2], flush=True)
                if not idx and mismatches:
                    i = mismatches[0] - 1
                    print(
                        "expected",
                        str(inputs[i]["expected"])[:650],
                        "actual",
                        str(outcomes[i])[:650],
                        flush=True,
                    )
                count += 1
    return int(bool(count))


if __name__ == "__main__":
    raise SystemExit(main())

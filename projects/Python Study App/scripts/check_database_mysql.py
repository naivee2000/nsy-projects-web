"""Find incorrect or ineffective SQL variants before the slower end-to-end UI sweep."""

import os
import sys
from code_practice.database_catalog import CATALOG
from code_practice.database_judge import matches
from scripts.database_oracle import query_tables


def main():
    container = os.environ.get("CODE_PRACTICE_MYSQL_CONTAINER", "")
    if not container.startswith("nsy-study-mysql-") or container.startswith(
        "nsy-study-mysql-production"
    ):
        raise SystemExit("Use a local test container.")
    failed = 0
    for key in map(int, sys.argv[1:]):
        p = CATALOG[key]
        try:
            runs, _ = query_tables(
                p["schema"], [c["tables"] for c in p["cases"]], [p["sql"], *p["wrong"]]
            )
            for idx, run in enumerate(runs):
                errors = [
                    i
                    for i, ((cols, rows), c) in enumerate(zip(run, p["cases"]), 1)
                    if not matches(
                        c["expected"],
                        cols or c["expected"]["columns"],
                        rows,
                        ordered=p["ordered"],
                        numeric_strings=True,
                    )
                ]
                if bool(errors) != bool(idx):
                    print(key, idx, "mismatches", errors, flush=True)
                    failed += 1
        except Exception as error:
            print(key, str(error)[:300], flush=True)
            failed += 1
    return int(bool(failed))


if __name__ == "__main__":
    raise SystemExit(main())

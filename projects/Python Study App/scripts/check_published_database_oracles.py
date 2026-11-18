"""Evaluate the separately published Pandas implementations used as offline example oracles.

Run without Docker/production access, with the study project's vetted source snapshot.
Packaging verifies the input hash before consuming these results.
"""

import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import re
import pandas as pd

from scripts.database_source_examples import read_source
from scripts.build_database_exercises import SETS, question_inputs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("ids", nargs="*", type=int)
    args = parser.parse_args()
    pins = json.loads(Path("scripts/database_oracle_pins.json").read_text())
    errors = 0
    args.out.mkdir(parents=True, exist_ok=True)
    for k in args.ids or sorted(map(int, pins)):
        try:
            path = args.source / f"{k}.md"
            source = re.findall(r"^```python\n(.*?)^```", path.read_text(), re.M | re.S)[0]
            if sha256(source.encode()).hexdigest() != pins[str(k)]:
                raise ValueError("Unrecognized independent implementation")
            if k == 3611:
                # The published statement specifies strictly more than twenty hours.
                source = source.replace('["hours"] >= 20', '["hours"] > 20')
            if k == 3673:
                source = source.replace(
                    '["session_duration_minutes"] >= 30', '["session_duration_minutes"] > 30'
                )
            if k == 3832:
                source = source.replace(
                    "['streak_length', 'user_id'], ascending=[False, True]",
                    "['streak_length', 'user_id', 'action', 'start_date'], ascending=[False, True, True, False]",
                )
            schema, ex = read_source(path)
            inputs = question_inputs(k, schema, ex[0], SETS[k][0])
            impl = {}
            exec(compile(source, "published-oracle-" + str(k), "exec"), impl)
            name = next(
                node.name for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)
            )
            outputs = []
            for tables in inputs:
                frames = {}
                for table, cols in schema.items():
                    frame = pd.DataFrame(tables[table], columns=[name for name, _ in cols])
                    for col, kind in cols:
                        if kind.startswith(("DATE", "TIMESTAMP")):
                            frame[col] = pd.to_datetime(frame[col], format="mixed")
                    frames[table] = frame
                df = impl[name](**frames)

                def cell(v):
                    if pd.isna(v):
                        return None
                    if isinstance(v, pd.Timestamp):
                        return (
                            v.isoformat(sep=" ")
                            if v.time().isoformat() != "00:00:00"
                            else v.date().isoformat()
                        )
                    return v.item() if hasattr(v, "item") else v

                outputs.append(
                    (
                        list(df.columns),
                        [[cell(v) for v in row] for row in df.itertuples(index=False, name=None)],
                    )
                )
            (args.out / f"{k}-pandas.json").write_text(
                json.dumps(
                    {
                        "inputs": sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest(),
                        "source": pins[str(k)],
                        "outputs": outputs,
                    },
                    allow_nan=False,
                )
            )
            print("Cross-checked Pandas inputs", k, flush=True)
        except Exception as error:
            print(k, type(error).__name__, str(error)[:700], flush=True)
            errors += 1
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())

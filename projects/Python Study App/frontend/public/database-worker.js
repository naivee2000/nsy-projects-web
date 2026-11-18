/* global importScripts, loadPyodide */
// Each run has its own interpreter and read-only package files.
importScripts("/pyodide/pyodide.js");

const harness = `
import io
import contextlib
import json
import pandas as pd

def pack(value):
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat(sep=" ")
    return value.item() if hasattr(value, "item") else value

def judge(source, schema, runner, inputs):
    cases = []
    program = compile(source, "<answer>", "exec")
    for case in inputs:
        try:
            tables = {}
            for name, table in case["tables"].items():
                data = pd.DataFrame(table["rows"], columns=table["columns"])
                for column, kind in schema[name]:
                    if "INT" in kind:
                        data[column] = data[column].astype("Int64")
                    elif kind.startswith(("DECIMAL", "FLOAT", "DOUBLE")):
                        data[column] = data[column].astype("Float64")
                    elif kind.startswith(("DATE", "TIMESTAMP")):
                        data[column] = pd.to_datetime(data[column])
                tables[name] = data
            scope = {"pd": pd}
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                exec(program, scope)
                answer = scope["solve"](*tables.values(), **case["parameters"])
            if runner == "mutation":
                if answer is not None:
                    raise TypeError("Modify the input table in place and return None.")
                answer = next(iter(tables.values()))
            if not isinstance(answer, pd.DataFrame):
                raise TypeError("Return a pandas DataFrame.")
            if answer.shape[0] > 5000 or answer.shape[1] > 128:
                raise ValueError("The result is too large.")
            cases.append({"actual": {"columns": list(map(str, answer.columns)),
                "rows": [[pack(value) for value in row] for row in answer.itertuples(index=False, name=None)]}})
        except Exception as error:
            cases.append({"error": str(error)[:900]})
    return json.dumps(cases, allow_nan=False, default=str)
`;

self.onmessage = async ({ data }) => {
  try {
    const py = await loadPyodide({
      indexURL: "/pyodide/",
      stdout: () => {},
      stderr: () => {},
    });
    await py.loadPackage("pandas");
    py.runPython(harness);
    self.postMessage({ ready: true });
    py.globals.set("input_json", JSON.stringify(data));
    const value = py.runPython(`
args = json.loads(input_json)
try:
    result = judge(args["source"], args["schema"], args["runner"], args["inputs"])
except SyntaxError as error:
    result = json.dumps([{"error": str(error)} for _ in args["inputs"]])
result
`);
    self.postMessage({ results: JSON.parse(value) });
  } catch (error) {
    self.postMessage({ error: String(error).slice(0, 900) });
  }
};

"""Install the matching, hash-checked Pyodide packages into the local build."""
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import urlopen

frontend = Path(__file__).resolve().parents[1] / "frontend"
lock = json.loads((frontend / "node_modules/pyodide/pyodide-lock.json").read_text())
version = lock["info"]["version"]
destination = frontend / "public" / "pyodide"
destination.mkdir(parents=True, exist_ok=True)


def install(name):
    spec = lock["packages"][name]
    for dependency in spec["depends"]:
        install(dependency)
    path = destination / spec["file_name"]
    if path.exists() and sha256(path.read_bytes()).hexdigest() == spec["sha256"]:
        return
    with urlopen(f"https://cdn.jsdelivr.net/pyodide/v{version}/full/{path.name}", timeout=90) as response:
        data = response.read()
    if sha256(data).hexdigest() != spec["sha256"]:
        raise ValueError(f"Hash mismatch for {path.name}")
    path.write_bytes(data)
    print(f"Installed {path.name}", flush=True)


install("pandas")

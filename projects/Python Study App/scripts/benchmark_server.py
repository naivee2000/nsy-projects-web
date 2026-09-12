"""Development-only loopback server with OS-reported process high-water memory.

The browser benchmark supplies an isolated database and a temporary report path.
This launcher is not imported by the application or used for normal studying.
"""
import argparse
import json
from pathlib import Path
import resource
import signal
import sys

import uvicorn


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--memory-report", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    # Uvicorn handles shutdown while serving, then replays captured signals to
    # the previous handlers. Allow that replay to finish so finally can report
    # the kernel high-water mark after all server work, including shutdown.
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: None)
    try:
        uvicorn.run("code_practice.app:app", host="127.0.0.1", port=args.port)
    finally:
        high_water = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # macOS reports bytes; Linux and other supported Unix platforms use KiB.
        peak_bytes = high_water if sys.platform == "darwin" else high_water * 1024
        args.memory_report.write_text(json.dumps({
            "peakRssBytes": peak_bytes,
            "method": "resource.getrusage(RUSAGE_SELF).ru_maxrss after server shutdown",
            "scope": "Backend process only; browser/Pyodide and benchmark driver excluded",
        }) + "\n")


if __name__ == "__main__":
    main()

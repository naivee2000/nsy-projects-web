"""Crash-safe writes for offline catalog artifacts, never for the progress DB."""
import json
import os
from pathlib import Path
import tempfile


def write_text_atomic(path: Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        # This exact temporary path belongs to this write operation only.
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_json_atomic(path: Path, payload) -> None:
    write_text_atomic(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

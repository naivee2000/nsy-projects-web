from __future__ import annotations

import os
from pathlib import Path
import threading


class LocalTokenStore:
    """Minimal machine-local credential file; the token is never returned by app APIs."""

    def __init__(self, data_dir: Path, filename: str = "marketdata_token", provider_label: str = "Market Data"):
        self.path = data_dir / filename
        self.provider_label = provider_label
        self._lock = threading.RLock()

    @property
    def exists(self) -> bool:
        return self.path.is_file()

    def load(self) -> str:
        with self._lock:
            try:
                return self.path.read_text(encoding="utf-8").strip()
            except FileNotFoundError:
                return ""
            except OSError as exc:
                raise RuntimeError(f"The saved {self.provider_label} token could not be read: {exc}") from exc

    def save(self, token: str) -> None:
        cleaned = token.strip()
        if not cleaned:
            raise ValueError(f"Paste a {self.provider_label} token before saving")
        if len(cleaned) > 8_192 or any(character.isspace() for character in cleaned):
            raise ValueError(f"The {self.provider_label} token contains unexpected whitespace or is too long")
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_name(f".{self.path.name}.{os.getpid()}.tmp")
            try:
                descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    handle.write(cleaned)
                    handle.write("\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, self.path)
                os.chmod(self.path, 0o600)
            finally:
                try:
                    temporary.unlink()
                except FileNotFoundError:
                    pass

    def delete(self) -> None:
        with self._lock:
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass

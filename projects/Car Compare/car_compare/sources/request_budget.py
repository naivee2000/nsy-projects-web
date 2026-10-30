"""Single-host, cross-process source budgets and bounded owned subprocesses.

All app jobs/workers must use the same local SQLite file. By default this is in
a per-user temporary directory; CAR_COMPARE_REQUEST_BUDGET_DB overrides it.
Slots are per normalized hostname (two total, not two per job). Cooldowns fail
fast, as before. Epoch deadlines are converted once to monotonic budgets.

Leases expire for owner revalidation, not for eviction of a live operation:
even a suspended worker must continue to count toward the two-slot limit.
Expired dead/reused-PID leases are reclaimed without a heartbeat or scheduler.
host_slot bounds acquisition only; callers must also bound their I/O. POSIX
run_bounded owns a new session and cleans its process group on every exit.
"""
from __future__ import annotations

from concurrent.futures import CancelledError
from contextlib import contextmanager
from email.utils import parsedate_to_datetime
from functools import lru_cache
import math
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import time
from urllib.parse import urlsplit
import uuid

COLLECTION_SECONDS = 12 * 60
MAX_SOURCE_OPERATIONS = 2
_POLL_SECONDS = 0.05


class SourceCoolingDown(RuntimeError):
    pass


class BudgetCancelled(CancelledError):
    """The caller's cancel_event was set, before launch or during a wait."""


class _Deadline:
    def __init__(self, epoch: float | None, maximum: float | None):
        seconds = maximum if epoch is None else float(epoch) - time.time()
        if seconds is None or not math.isfinite(seconds) or (maximum is not None and not math.isfinite(maximum)):
            raise ValueError("Deadline and timeout must be finite")
        self.seconds = max(0.0, seconds if maximum is None else min(seconds, maximum))
        self.end = time.monotonic() + self.seconds

    def remaining(self):
        return max(0.0, self.end - time.monotonic())

    def check(self, cancel_event=None):
        _check_cancelled(cancel_event)
        if not self.remaining():
            raise TimeoutError("Collection deadline reached while waiting for source")


def _check_cancelled(cancel_event):
    if cancel_event is not None and cancel_event.is_set():
        raise BudgetCancelled("Collection cancelled")


def _pause(seconds, cancel_event=None):
    if cancel_event is None:
        time.sleep(seconds)
    elif cancel_event.wait(seconds):
        raise BudgetCancelled("Collection cancelled")


@lru_cache(maxsize=1)
def _boot_id():
    if sys.platform.startswith("linux"):
        return Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    if sys.platform == "darwin":
        return subprocess.check_output(
            ["/usr/sbin/sysctl", "-n", "kern.boottime"], text=True, timeout=1,
        ).strip()
    raise NotImplementedError("Request budgets require Linux or macOS")


def _process_identity(pid):
    """Return a birth marker, None for dead/zombie, or '' if uninspectable."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return None
    except PermissionError:
        return ""
    try:
        if sys.platform.startswith("linux"):
            fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
            return None if fields[0] == "Z" else fields[19]
        result = subprocess.run(
            ["/bin/ps", "-p", str(pid), "-o", "lstart=", "-o", "stat="],
            capture_output=True, text=True, timeout=0.5, check=False,
        )
        if not result.stdout.strip():
            return None if result.returncode == 1 else ""
        birth, state = result.stdout.strip().rsplit(None, 1)
        return None if state.startswith("Z") else birth
    except FileNotFoundError:
        return None if sys.platform.startswith("linux") else ""
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
        return ""


@lru_cache(maxsize=16)
def _owner_identity(pid):
    # Keying by PID prevents forked workers from inheriting their parent's ID.
    return _process_identity(pid) or ""


def _host(url):
    return (urlsplit(url).hostname or "").lower().rstrip(".")


def _retry_seconds(retry_after):
    try:
        seconds = float(retry_after if retry_after not in (None, "") else 60)
    except (TypeError, ValueError, OverflowError):
        try:
            seconds = parsedate_to_datetime(str(retry_after)).timestamp() - time.time()
        except (TypeError, ValueError, OverflowError):
            seconds = 60
    return max(1.0, seconds) if math.isfinite(seconds) and seconds >= 0 else 60.0


def _default_path():
    configured = os.environ.get("CAR_COMPARE_REQUEST_BUDGET_DB")
    if configured:
        return Path(configured).expanduser().resolve()
    # Do not depend on cwd or TMPDIR, which may differ between app and workers.
    return Path("/tmp") / f"car-compare-budget-{os.getuid()}" / "budget.sqlite3"


class RequestBudget:
    """Local SQLite lease semaphore; construction opens no persistent connection.

    An explicit db_path is useful for isolated tests. All cooperating processes
    must share the path and lease_seconds (default 30). No network filesystems.
    """

    def __init__(self, db_path=None, *, poll_interval=0.05, lease_seconds=30.0):
        if not all(math.isfinite(v) and v > 0 for v in (poll_interval, lease_seconds)):
            raise ValueError("Poll interval and lease duration must be positive and finite")
        self.db_path = Path(db_path) if db_path is not None else _default_path()
        self.poll_interval = poll_interval
        self.lease_seconds = lease_seconds

    def _transaction(self, operation, deadline, cancel_event=None):
        deadline.check(cancel_event)
        boot = _boot_id()
        self.db_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        while True:
            deadline.check(cancel_event)
            connection = None
            try:
                connection = sqlite3.connect(str(self.db_path), timeout=0, isolation_level=None)
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    "CREATE TABLE IF NOT EXISTS leases ("
                    "token TEXT PRIMARY KEY, host TEXT NOT NULL, pid INTEGER NOT NULL, "
                    "birth TEXT NOT NULL, expires REAL NOT NULL, boot TEXT NOT NULL)"
                )
                connection.execute(
                    "CREATE TABLE IF NOT EXISTS cooldowns ("
                    "host TEXT PRIMARY KEY, until_at REAL NOT NULL, boot TEXT NOT NULL)"
                )
                connection.execute("DELETE FROM leases WHERE boot != ?", (boot,))
                connection.execute("DELETE FROM cooldowns WHERE boot != ?", (boot,))
                result = operation(connection, boot)
                deadline.check(cancel_event)
                connection.commit()
                return result
            except sqlite3.OperationalError as exc:
                if getattr(exc, "sqlite_errorcode", None) not in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
                    raise
            finally:
                if connection is not None:
                    connection.close()
            _pause(min(self.poll_interval, deadline.remaining()), cancel_event)

    def rate_limited(self, url, retry_after=None):
        host = _host(url)
        until = time.monotonic() + _retry_seconds(retry_after)

        def record(connection, boot):
            connection.execute(
                "INSERT INTO cooldowns VALUES (?, ?, ?) ON CONFLICT(host) DO UPDATE SET "
                "until_at = MAX(cooldowns.until_at, excluded.until_at)", (host, until, boot),
            )

        self._transaction(record, _Deadline(None, 30))

    @contextmanager
    def host_slot(self, url, deadline=None, *, cancel_event=None):
        # An explicit deadline may exceed the legacy default 30-second wait.
        end = _Deadline(deadline, 30 if deadline is None else None)
        end.check(cancel_event)
        host, token, pid = _host(url), uuid.uuid4().hex, os.getpid()
        birth = _owner_identity(pid)

        def acquire(connection, boot):
            now = time.monotonic()
            cooldown = connection.execute(
                "SELECT until_at FROM cooldowns WHERE host = ?", (host,),
            ).fetchone()
            if cooldown and cooldown[0] > now:
                raise SourceCoolingDown(
                    f"{host} rate limited; retry after {math.ceil(cooldown[0] - now)}s"
                )
            rows = connection.execute(
                "SELECT token, pid, birth FROM leases WHERE host = ? AND expires <= ?",
                (host, now),
            ).fetchall()
            for lease_token, owner_pid, owner_birth in rows:
                identity = birth if owner_pid == pid else _process_identity(owner_pid)
                if identity is None or (identity and owner_birth and identity != owner_birth):
                    connection.execute("DELETE FROM leases WHERE token = ?", (lease_token,))
                else:
                    connection.execute(
                        "UPDATE leases SET expires = ? WHERE token = ?",
                        (time.monotonic() + self.lease_seconds, lease_token),
                    )
            count = connection.execute(
                "SELECT COUNT(*) FROM leases WHERE host = ?", (host,),
            ).fetchone()[0]
            if count >= MAX_SOURCE_OPERATIONS:
                return False
            connection.execute(
                "INSERT INTO leases VALUES (?, ?, ?, ?, ?, ?)",
                (token, host, pid, birth, time.monotonic() + self.lease_seconds, boot),
            )
            return True

        while not self._transaction(acquire, end, cancel_event):
            _pause(min(self.poll_interval, end.remaining()), cancel_event)
        try:
            end.check(cancel_event)
            yield
        finally:
            # Release ignores the expired/cancelled caller's budget, but cannot
            # hang indefinitely on an externally locked/corrupt database.
            self._transaction(
                lambda connection, boot: connection.execute(
                    "DELETE FROM leases WHERE token = ?", (token,),
                ), _Deadline(None, 5),
            )


@contextmanager
def host_slot(url: str, deadline: float | None = None, *, cancel_event=None):
    """Acquire a shared host slot; epoch deadline defaults to a 30s wait cap."""
    with RequestBudget().host_slot(url, deadline, cancel_event=cancel_event):
        yield


def rate_limited(url: str, retry_after: str | None = None) -> None:
    """Share a Retry-After seconds/HTTP-date cooldown, defaulting to 60s."""
    RequestBudget().rate_limited(url, retry_after)


def start_owned_process(command, **kwargs):
    """Start a POSIX worker in a new session, recording ownership for cleanup.

    For caller-managed Popen loops. These callers must enforce their deadline
    and call terminate_owned_process in finally, including on normal exit.
    """
    if os.name != "posix":
        raise NotImplementedError("Owned process groups require POSIX")
    if kwargs.get("start_new_session", True) is not True:
        raise ValueError("Owned workers require start_new_session=True")
    if "preexec_fn" in kwargs or "process_group" in kwargs:
        raise ValueError("Owned workers control process-group configuration")
    kwargs["start_new_session"] = True
    process = subprocess.Popen(command, **kwargs)
    process._request_budget_owner = os.getpid()
    return process


def terminate_owned_process(process, *, grace_seconds=0.2):
    """TERM then KILL only a group created by start_owned_process here.

    Cleanup can take grace_seconds plus up to one second to reap the child.
    Descendants must not deliberately escape the owned session/process group.
    """
    if getattr(process, "_request_budget_owner", None) != os.getpid():
        raise ValueError("Refusing to terminate a process group not owned by this helper")
    if not math.isfinite(grace_seconds) or grace_seconds < 0:
        raise ValueError("Grace period must be nonnegative and finite")
    group = process.pid
    try:
        os.killpg(group, signal.SIGTERM)
    except ProcessLookupError:
        pass
    else:
        end = time.monotonic() + grace_seconds
        while time.monotonic() < end:
            process.poll()
            try:
                os.killpg(group, 0)
            except ProcessLookupError:
                break
            time.sleep(min(0.01, max(0, end - time.monotonic())))
        try:
            os.killpg(group, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait(timeout=1)


def terminate_process_group(process, *, grace_seconds=0.2):
    """Alias for terminate_owned_process; does not accept arbitrary Popen objects."""
    return terminate_owned_process(process, grace_seconds=grace_seconds)


def run_bounded(command, *, deadline_at=None, cancel_event=None, timeout=None, **kwargs):
    """subprocess.run-style result with cancellation and a hard 12-minute cap.

    deadline_at is epoch seconds. timeout can impose a shorter relative cap.
    Expiry raises subprocess.TimeoutExpired (including captured partial output);
    cancellation raises BudgetCancelled. Already expired/cancelled calls never
    launch. Supports run's input/capture_output/check and Popen keyword options.
    start_new_session must be True; preexec_fn/process_group are disallowed so
    cleanup always targets only this invocation's owned group. POSIX only.
    """
    if os.name != "posix":
        raise NotImplementedError("Owned process groups require POSIX")
    maximum = COLLECTION_SECONDS if timeout is None else min(COLLECTION_SECONDS, float(timeout))
    if timeout is not None and not math.isfinite(float(timeout)):
        raise ValueError("Timeout must be finite")
    end = _Deadline(deadline_at, maximum)
    _check_cancelled(cancel_event)
    if not end.remaining():
        raise subprocess.TimeoutExpired(command, end.seconds)
    input_data = kwargs.pop("input", None)
    check = kwargs.pop("check", False)
    if input_data is not None:
        if kwargs.get("stdin") is not None:
            raise ValueError("stdin and input arguments may not both be used")
        kwargs["stdin"] = subprocess.PIPE
    if kwargs.pop("capture_output", False):
        if kwargs.get("stdout") is not None or kwargs.get("stderr") is not None:
            raise ValueError("stdout/stderr may not be used with capture_output")
        kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _check_cancelled(cancel_event)
    if not end.remaining():
        raise subprocess.TimeoutExpired(command, end.seconds)
    process = start_owned_process(command, **kwargs)
    stdout = stderr = None
    try:
        while True:
            _check_cancelled(cancel_event)
            remaining = end.remaining()
            if not remaining:
                raise subprocess.TimeoutExpired(command, end.seconds, output=stdout, stderr=stderr)
            try:
                stdout, stderr = process.communicate(input_data, timeout=min(_POLL_SECONDS, remaining))
                break
            except subprocess.TimeoutExpired as exc:
                stdout, stderr = exc.output, exc.stderr
                input_data = None
        _check_cancelled(cancel_event)
        if not end.remaining():
            raise subprocess.TimeoutExpired(command, end.seconds, output=stdout, stderr=stderr)
    finally:
        try:
            terminate_owned_process(process)
        finally:
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream is not None:
                    stream.close()
    result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
    if check:
        result.check_returncode()
    return result

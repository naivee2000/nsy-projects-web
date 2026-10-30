import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from car_compare.sources.request_budget import RequestBudget, SourceCoolingDown, BudgetCancelled, run_bounded
from car_compare.sources.request_budget import _Deadline, _retry_seconds


class RequestBudgetTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.budget = RequestBudget(Path(directory.name) / "budget.sqlite3", poll_interval=0.005)
        for p in (patch("car_compare.sources.request_budget._boot_id", return_value="test-boot"), patch("car_compare.sources.request_budget._owner_identity", return_value="test-process")):
            p.start()
            self.addCleanup(p.stop)

    def test_two_operations_shared_by_separate_budget_instances(self):
        other = RequestBudget(self.budget.db_path, poll_interval=0.005)
        with self.budget.host_slot("https://visor.vin/a"), other.host_slot("https://visor.vin/b"):
            with self.assertRaises(TimeoutError):
                with other.host_slot("https://visor.vin/c", time.time() + .04):
                    self.fail("Third operation acquired a slot")
        with other.host_slot("https://visor.vin/c", time.time() + .1):
            pass

    def test_cooldown_shared_and_other_host_unaffected(self):
        self.budget.rate_limited("https://visor.vin/a", "60")
        with self.assertRaises(SourceCoolingDown):
            with RequestBudget(self.budget.db_path).host_slot("https://visor.vin/b"):
                self.fail("Cooldown ignored")
        with self.budget.host_slot("https://edmunds.com/"):
            pass

    def test_expired_and_cancelled_never_acquire(self):
        with self.assertRaises(TimeoutError):
            with self.budget.host_slot("https://visor.vin", time.time() - 1):
                self.fail()
        cancelled = threading.Event()
        cancelled.set()
        with self.assertRaises(BudgetCancelled):
            with self.budget.host_slot("https://visor.vin", cancel_event=cancelled):
                self.fail()

    def test_expired_process_never_starts(self):
        with patch("car_compare.sources.request_budget.subprocess.Popen") as spawn:
            with self.assertRaises(subprocess.TimeoutExpired):
                run_bounded([sys.executable, "-c", "pass"], deadline_at=time.time() - 1)
            spawn.assert_not_called()

    def test_process_timeout_and_success(self):
        start = time.monotonic()
        with self.assertRaises(subprocess.TimeoutExpired):
            run_bounded([sys.executable, "-c", "import time; time.sleep(10)"], timeout=.1, capture_output=True, text=True)
        self.assertLess(time.monotonic() - start, 2)
        result = run_bounded([sys.executable, "-c", "print('ok')"], timeout=2, capture_output=True, text=True)
        self.assertEqual(result.stdout.strip(), "ok")
        self.assertEqual(result.returncode, 0)

    def test_cancellation_terminates_running_process(self):
        cancelled = threading.Event()
        timer = threading.Timer(.1, cancelled.set)
        timer.start()
        try:
            with self.assertRaises(BudgetCancelled):
                run_bounded([sys.executable, "-c", "import time; time.sleep(10)"], timeout=2, cancel_event=cancelled)
        finally:
            timer.join()

    def test_two_slots_are_enforced_in_another_process(self):
        script = """
import sys, time
from car_compare.sources import request_budget as budget
budget._boot_id = lambda: 'test-boot'
budget._owner_identity = lambda pid: 'test-process'
try:
    with budget.RequestBudget(sys.argv[1], poll_interval=.005).host_slot('https://visor.vin', time.time()+.1):
        print('acquired')
except TimeoutError:
    print('limited')
"""
        with self.budget.host_slot("https://visor.vin/a"), self.budget.host_slot("https://visor.vin/b"):
            result = run_bounded([sys.executable, "-c", script, str(self.budget.db_path)], timeout=3, text=True, capture_output=True)
            self.assertEqual(result.stdout.strip(), "limited", result.stderr)
        result = run_bounded([sys.executable, "-c", script, str(self.budget.db_path)], timeout=3, text=True, capture_output=True)
        self.assertEqual(result.stdout.strip(), "acquired", result.stderr)

    def test_deadline_uses_monotonic_clock_after_creation(self):
        with patch("car_compare.sources.request_budget.time.time", return_value=100), patch("car_compare.sources.request_budget.time.monotonic", return_value=10):
            deadline = _Deadline(105, None)
        with patch("car_compare.sources.request_budget.time.time", return_value=-10000), patch("car_compare.sources.request_budget.time.monotonic", return_value=16):
            with self.assertRaises(TimeoutError):
                deadline.check()

    def test_retry_after_date_and_invalid_default(self):
        with patch("car_compare.sources.request_budget.time.time", return_value=0):
            self.assertEqual(_retry_seconds("Thu, 01 Jan 1970 00:02:00 GMT"), 120)
        for value in (None, "invalid", "NaN", "-1"):
            self.assertEqual(_retry_seconds(value), 60)

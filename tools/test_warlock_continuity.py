"""Local mocked-queue tests; no worker, service, model, native or Codex execution."""
from datetime import datetime, timezone
import json
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

import warlock_continuity as policy


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / "config.json"
        self.checkpoint = self.root / "checkpoint.json"
        self.now = 2000000000.0
        self.config = dict(schema=1, mode="unattended", thread="d996c48c-dabb-47d6-b8fc-2100f1e9a689",
                           repo=str(self.root), codex="/bin/true", checkpoint=str(self.checkpoint),
                           expiresUTC=datetime.fromtimestamp(self.now + 1000, timezone.utc).isoformat())
        self.write(self.path, self.config)
        self.write_checkpoint({}, age=301)
        self.queue = Mock(return_value=subprocess.CompletedProcess([], 0, "queued", ""))

    def write(self, path, value):
        path.write_text(json.dumps(value))
        path.chmod(0o600)

    def write_checkpoint(self, data, age=0):
        self.write(self.checkpoint, data)
        os.utime(self.checkpoint, (self.now - age, self.now - age))

    def tick(self):
        with policy.singleton(self.path):
            return policy.tick(self.path, clock=lambda: self.now, runner=self.queue)

    def test_handoff_is_default_and_does_not_read_checkpoint(self):
        self.write(self.path, {"schema": 1})
        self.checkpoint.unlink()
        self.assertEqual(self.tick()["status"], "disarmed")
        self.queue.assert_not_called()

    def test_expired_never_queues(self):
        self.config["expiresUTC"] = datetime.fromtimestamp(self.now, timezone.utc).isoformat()
        self.write(self.path, self.config)
        self.assertEqual(self.tick()["status"], "expired")
        self.queue.assert_not_called()

    def test_fresh_checkpoint_does_not_queue(self):
        self.write_checkpoint({}, age=300)
        self.assertEqual(self.tick()["status"], "fresh")
        self.queue.assert_not_called()

    def test_stale_queues_only_fixed_existing_thread_argv(self):
        result = self.tick()
        self.assertEqual(result["status"], "wake-unconfirmed")
        self.assertTrue(result["queueAccepted"])
        self.assertFalse(result["restartVerified"])
        args, kwargs = self.queue.call_args
        self.assertEqual(args[0], ["/bin/true", "queue", "--thread", self.config["thread"],
                                  "--message", policy.PROMPT, "--resume", "-C", str(self.root)])
        self.assertNotIn("shell", kwargs)
        self.assertEqual(kwargs["timeout"], 20)

    def test_running_with_terminal_report_queues_even_when_fresh(self):
        report = self.root / "report.json"
        self.write(report, {"passed": False, "error": "completed failing check"})
        self.write_checkpoint({"activeVerification": {"status": "ACTUALLYRUNNING", "report": "report.json"}})
        self.assertEqual(self.tick()["reason"], "running-checkpoint-has-terminal-report")
        self.queue.assert_called_once()

    def test_initial_false_report_is_not_terminal(self):
        self.write(self.root / "report.json", {"passed": False, "commands": []})
        self.write_checkpoint({"activeVerification": {"status": "RUNNING", "report": "report.json"}})
        self.assertEqual(self.tick()["status"], "fresh")
        self.queue.assert_not_called()

    def test_explicit_paused_and_complete_goal_never_queues(self):
        for status in ("paused", "complete", "completed", "stopped", "cancelled", "canceled"):
            self.write_checkpoint({"goalStatus": status}, age=1000)
            self.assertEqual(self.tick()["status"], "goal-quiescent")
        self.queue.assert_not_called()

    def test_actual_external_blocker_never_queues(self):
        self.write_checkpoint({"goalStatus": "blocked", "externalBlocker": True}, age=1000)
        self.assertEqual(self.tick()["status"], "external-blocked")
        self.queue.assert_not_called()

    def test_internal_blocked_goal_still_requests_repair(self):
        self.write_checkpoint({"goalStatus": "blocked", "externalBlocker": False}, age=1000)
        self.assertTrue(self.tick()["queueAccepted"])

    def test_checkpoint_pause_during_observation_prevents_queue(self):
        original = policy.load_config
        calls = 0

        def load(path):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.write_checkpoint({"goalStatus": "paused"})
            return original(path)

        with patch.object(policy, "load_config", side_effect=load):
            self.assertEqual(self.tick()["status"], "checkpoint-changed")
        self.queue.assert_not_called()

    def test_watch_exits_when_authorization_is_quiescent(self):
        for status in ("disarmed", "expired", "goal-quiescent", "external-blocked"):
            with self.subTest(status=status), \
                    patch("sys.argv", ["guard", "--config", str(self.path), "--watch"]), \
                    patch.object(policy, "tick", return_value={"status": status}) as tick, \
                    patch.object(policy.time, "sleep") as sleep, \
                    patch("sys.stdout", io.StringIO()):
                self.assertEqual(policy.main(), 0)
                tick.assert_called_once()
                sleep.assert_not_called()

    def test_watch_retries_after_transient_invalid_snapshot(self):
        output = io.StringIO()
        with patch("sys.argv", ["guard", "--config", str(self.path), "--watch"]), \
                patch.object(policy, "tick", side_effect=[ValueError("partial write"), {"status": "fresh"}]) as tick, \
                patch.object(policy.time, "sleep", side_effect=[None, KeyboardInterrupt]), \
                patch("sys.stdout", output):
            self.assertEqual(policy.main(), 0)
        self.assertEqual(tick.call_count, 2)
        self.assertEqual([json.loads(line)["status"] for line in output.getvalue().splitlines()],
                         ["invalid-state", "fresh"])
        self.queue.assert_not_called()

    def test_failed_resume_is_a_nonzero_one_shot_result(self):
        with patch("sys.argv", ["guard", "--config", str(self.path), "--once"]), \
                patch.object(policy, "tick", return_value={"status": "wake-unconfirmed",
                    "queueAttempted": True, "queueAccepted": False}), patch("sys.stdout", io.StringIO()):
            self.assertEqual(policy.main(), 4)

    def test_cooldown_persists_and_reserves_failed_attempt(self):
        self.queue.side_effect = subprocess.TimeoutExpired("codex", 20)
        self.assertEqual(self.tick()["queueFailure"], "TimeoutExpired")
        self.assertEqual(self.tick()["status"], "cooldown")
        self.now += 300
        self.assertEqual(self.tick()["queueFailure"], "TimeoutExpired")
        self.assertEqual(self.queue.call_count, 2)

    def test_warning_exit_zero_and_nonzero_are_unconfirmed(self):
        for code, stdout, stderr in [(0, "", "WARN resume failed"), (1, "", "refused")]:
            with self.subTest(code=code):
                self.queue.return_value = subprocess.CompletedProcess([], code, stdout, stderr)
                result = self.tick()
                self.assertFalse(result["queueAccepted"])
                self.assertFalse(result["restartVerified"])
                self.now += 300

    def test_singleton_second_watcher_cannot_dispatch(self):
        with policy.singleton(self.path):
            with self.assertRaises(BlockingIOError):
                self.tick()
        self.queue.assert_not_called()

    def test_invalid_uuid_or_config_permissions_refuse(self):
        self.config["thread"] = "not-a-thread; command"
        self.write(self.path, self.config)
        with self.assertRaises(ValueError):
            self.tick()
        self.write(self.path, {"schema": 1})
        self.path.chmod(0o644)
        with self.assertRaises(ValueError):
            self.tick()
        self.queue.assert_not_called()

    def test_config_expiry_during_observation_does_not_dispatch(self):
        expires = datetime.fromisoformat(self.config["expiresUTC"]).timestamp()
        clock = Mock(side_effect=[self.now, expires])
        with policy.singleton(self.path):
            self.assertEqual(policy.tick(self.path, clock=clock, runner=self.queue)["status"],
                             "config-changed-or-expired")
        self.queue.assert_not_called()


if __name__ == "__main__":
    unittest.main()

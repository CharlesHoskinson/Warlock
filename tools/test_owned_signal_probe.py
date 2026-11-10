#!/usr/bin/env python3
"""Root-only pure controls. Process, selector, clock and native effects mocked."""
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

SOURCE = Path(os.environ.get("WARLOCK_SIGNAL_RUNNER_UNDER_TEST", str(Path(__file__).with_name("run_owned_signal_probe.py"))))
SPEC = importlib.util.spec_from_file_location("owned_signal_runner_under_test", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Missing fixed runner loader")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
NORMAL = b"callback-thread=ThreadId 7\nowned-signal-lifecycle: complete\n"


class Selector:
    def __init__(self, step):
        self.keys = {}
        self.step = step
        self.timeouts = []

    def register(self, pipe, _events, label):
        self.keys[pipe.fileno()] = SimpleNamespace(fd=pipe.fileno(), fileobj=pipe, data=label)

    def unregister(self, pipe):
        del self.keys[pipe.fileno()]

    def get_map(self):
        return self.keys

    def select(self, timeout):
        self.timeouts.append(timeout)
        self.step()
        return [(key, None) for key in list(self.keys.values())]

    def close(self):
        pass


class ClockCollectorTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.output = self.root / ".warlock-contributor" / "owned-signal-probe-fixture"
        self.output.mkdir(parents=True, mode=0o700)
        self.image = self.output / "owned-signal-lifecycle-controls"
        self.image.write_bytes(b"fixture-only")
        self.now = 100_000_000_000
        self.utc = runner.EXPIRY_NS - 10_000_000_000
        self.mock(runner, "ROOT", new=self.root)
        self.mock(runner.time, "monotonic_ns", side_effect=lambda: self.now)
        self.mock(runner.time, "time_ns", side_effect=lambda: self.utc)
        self.boot = self.mock(runner, "boot_id", return_value="same-boot")
        self.child = Mock(pid=999)
        self.child.stdout = Mock()
        self.child.stderr = Mock()
        self.child.stdout.fileno.return_value = 11
        self.child.stderr.fileno.return_value = 12
        self.child.wait.return_value = 0
        self.spawn = self.mock(runner.subprocess, "Popen", return_value=self.child)
        self.mock(runner.subprocess, "run", side_effect=AssertionError("No real subprocess"))
        self.kill = self.mock(runner.os, "killpg")
        self.chunks = {11: [NORMAL, b""], 12: [b""]}
        self.mock(runner.os, "read", side_effect=lambda fd, _size: self.chunks[fd].pop(0))
        self.selector = Selector(lambda: None)
        self.mock(runner.selectors, "DefaultSelector", return_value=self.selector)

    def mock(self, target, name, **kwargs):
        item = patch.object(target, name, **kwargs)
        value = item.start()
        self.addCleanup(item.stop)
        return value

    def test_literal_single_origin_and_human_reserve(self):
        self.utc = runner.EXPIRY_NS - 6_000_000_000
        budget = runner.sample_budget()
        self.assertEqual(budget["originNs"], 100_000_000_000)
        self.assertEqual(budget["deadlineNs"], 104_000_000_000)
        self.assertEqual(budget["cleanupLimitNs"], 106_000_000_000)

    def test_insufficient_human_window_refuses(self):
        for left in (2_000_000_000, 0, -1):
            with self.subTest(left=left):
                self.utc = runner.EXPIRY_NS - left
                with self.assertRaises(ValueError):
                    runner.sample_budget()
        self.spawn.assert_not_called()

    def test_setup_consumes_cap_and_same_D_reaches_fixture_and_wait(self):
        budget = runner.sample_budget()
        self.now = 102_000_000_000
        outcome, stdout, stderr = runner.collect(self.image, self.output, budget)
        self.assertTrue(outcome["passed"])
        self.assertEqual((stdout, stderr), (NORMAL, b""))
        self.assertEqual(self.spawn.call_args.args[0][-2:], ["/probe", "105000000000"])
        self.child.wait.assert_called_once_with(timeout=3.0)
        self.assertEqual(outcome["deadlineNs"], 105_000_000_000)
        self.kill.assert_not_called()

    def test_regression_and_boot_change_refuse_before_spawn(self):
        budget = runner.sample_budget()
        self.now -= 1
        outcome, _, _ = runner.collect(self.image, self.output, budget)
        self.assertFalse(outcome["passed"])
        self.spawn.assert_not_called()
        self.now = 100_000_000_000
        self.boot.return_value = "other-boot"
        with self.assertRaises(ValueError):
            runner.remaining_ns(budget)

    def test_wall_regression_and_negative_monotonic_refuse(self):
        budget = runner.sample_budget()
        self.utc -= 1
        with self.assertRaises(ValueError):
            runner.remaining_ns(budget)
        self.now = -1
        with self.assertRaises(ValueError):
            runner.sample_budget()

    def test_late_EOF_is_failure_even_with_normal_exit(self):
        budget = runner.sample_budget()
        self.selector.step = lambda: setattr(self, "now", 105_000_000_000)
        outcome, _, _ = runner.collect(self.image, self.output, budget)
        self.assertFalse(outcome["passed"])
        self.assertTrue(outcome["timeout"])
        self.assertTrue(outcome["forcedCleanup"])
        self.assertEqual(outcome["cleanupDeadlineNs"], 107_000_000_000)
        self.child.wait.assert_called_once_with(timeout=2.0)

    def test_early_failure_cleanup_never_gets_more_than_two_seconds(self):
        budget = runner.sample_budget()
        self.chunks[11] = [b"x" * 65537]
        outcome, stdout, _ = runner.collect(self.image, self.output, budget)
        self.assertFalse(outcome["passed"])
        self.assertEqual(outcome["cleanupDeadlineNs"], 102_000_000_000)
        self.assertLessEqual(len(stdout), 65536)
        self.child.wait.assert_called_once_with(timeout=2.0)

    def test_unknown_reap_remains_failed(self):
        budget = runner.sample_budget()
        self.chunks[11] = [b"x" * 65537]
        self.child.wait.side_effect = runner.subprocess.TimeoutExpired("fixed-child", 2)
        outcome, _, _ = runner.collect(self.image, self.output, budget)
        self.assertFalse(outcome["passed"])
        self.assertTrue(outcome["cleanupUnknown"])
        self.assertFalse(outcome["reaped"])

    def test_cleanup_exhaustion_does_not_start_new_wait(self):
        budget = runner.sample_budget()
        self.selector.step = lambda: setattr(self, "now", 107_000_000_000)
        outcome, _, _ = runner.collect(self.image, self.output, budget)
        self.assertFalse(outcome["passed"])
        self.assertTrue(outcome["cleanupUnknown"])
        self.child.wait.assert_not_called()

    def test_nonzero_exit_never_passes_or_kills_reaped_pid(self):
        self.child.wait.return_value = 1
        outcome, _, _ = runner.collect(self.image, self.output, runner.sample_budget())
        self.assertFalse(outcome["passed"])
        self.assertTrue(outcome["reaped"])
        self.kill.assert_not_called()

    def test_literal_output_refusals(self):
        for stdout, stderr in [(NORMAL + b"x", b""), (NORMAL[:-1], b""),
                               (NORMAL + NORMAL, b""), (NORMAL, b"x"),
                               (b'{}\n', b""), (NORMAL.replace(b" 7", b" NaN"), b"")]:
            with self.subTest(stdout=stdout, stderr=stderr):
                with self.assertRaises(ValueError):
                    runner.validate_output(stdout, stderr)
        runner.validate_output(NORMAL, b"")

    def test_combined_output_limit_counts_both_streams(self):
        self.chunks = {11: [b"x" * 65535], 12: [b"xx"]}
        outcome, stdout, stderr = runner.collect(self.image, self.output, runner.sample_budget())
        self.assertFalse(outcome["passed"])
        self.assertLessEqual(len(stdout) + len(stderr), 65536)

    def test_fixed_command_has_one_D_no_time_namespace_display_or_network(self):
        command = runner.fixed_command(self.image, runner.sample_budget())
        self.assertEqual(command[-3:], ["--", "/probe", "105000000000"])
        self.assertIn("--unshare-net", command)
        self.assertIn("--unshare-pid", command)
        self.assertNotIn("--unshare-time", command)
        self.assertNotIn("DISPLAY", command)
        self.assertNotIn("WAYLAND_DISPLAY", command)
        self.assertEqual(command.count("105000000000"), 1)

    def test_image_replaced_or_insecure_metadata_refused(self):
        data = bytearray(64)
        data[:7] = b"\x7fELF\x02\x01\x01"
        data[18:20] = (183).to_bytes(2, "little")
        self.image.write_bytes(data)
        self.image.chmod(0o500)
        observed, _ = runner.image_binding(self.image)
        runner.check_image(self.image, observed)
        for field in ("device", "inode", "size", "uid", "mode"):
            wrong = dict(observed, **{field: observed[field] + 1})
            with self.subTest(field=field), self.assertRaises(ValueError):
                runner.check_image(self.image, wrong)
        self.image.chmod(0o4700)
        with self.assertRaises(ValueError):
            runner.image_binding(self.image)

    def test_wrong_arch_symlink_and_non_executable_refused(self):
        self.image.chmod(0o400)
        with self.assertRaises(ValueError):
            runner.image_binding(self.image)
        self.image.chmod(0o500)
        with self.assertRaises(ValueError):
            runner.image_binding(self.image)
        target = self.image.with_name("other")
        self.image.rename(target)
        self.image.symlink_to(target)
        with self.assertRaises(ValueError):
            runner.image_binding(self.image)

    def packet_fixture(self):
        return {'schema': 1, 'kind': 'fixed-cold-owned-signal', 'record': runner.RECORD,
                'recordIdentitySha256': runner.IDENTITY, 'selectionGeneration': runner.GENERATION,
                'authorizationExpiresUTC': runner.EXPIRY, 'systemInventorySha256': 'fixture-sdk',
                'sourceHashes': {}, 'image': None, 'buildReport': None}

    def test_unknown_packet_fields_and_wrong_identity_refuse_before_source_or_spawn(self):
        check = self.mock(runner, 'verify_sources', side_effect=AssertionError('Shape must refuse first'))
        for key, value in [('command', ['/bin/true']), ('schema', True), ('selectionGeneration', True),
                           ('recordIdentitySha256', 'foreign'), ('authorizationExpiresUTC', 'later'),
                           ('kind', 'fixed-webkit-provider-probe'), ('systemInventorySha256', 'other')]:
            packet = dict(self.packet_fixture(), **{key: value})
            raw = json.dumps(packet).encode()
            helper = SimpleNamespace(SYSTEM_SHA='fixture-sdk', unique=dict, regular=lambda *_: raw)
            with self.subTest(key=key), self.assertRaises(ValueError):
                runner.read_packet(helper, runner.digest(raw))
        check.assert_not_called()
        self.spawn.assert_not_called()

    def test_null_future_image_never_authorizes_execution(self):
        self.mock(runner, 'verify_sources')
        raw = json.dumps(self.packet_fixture()).encode()
        helper = SimpleNamespace(SYSTEM_SHA='fixture-sdk', unique=dict, regular=lambda *_: raw)
        with self.assertRaises(ValueError):
            runner.read_packet(helper, runner.digest(raw))
        self.spawn.assert_not_called()

    def test_source_map_and_actual_content_drift_refuse(self):
        helper = SimpleNamespace(regular=Mock(return_value=b'wrong'))
        with self.assertRaises(ValueError):
            runner.verify_sources(helper, {})
        helper.regular.assert_not_called()
        sources = {'fixed/file': runner.digest(b'expected')}
        self.mock(runner, 'SOURCE_MAP_SHA', new=runner.map_digest(sources))
        with self.assertRaises(ValueError):
            runner.verify_sources(helper, sources)
        helper.regular.return_value = b'expected'
        runner.verify_sources(helper, sources)

    def test_build_report_source_and_image_crossrefs_are_required(self):
        self.mock(runner, 'verify_sources')
        self.mock(runner, 'check_image', return_value=b'not-executed')
        sources = {'source': 'literal-expected'}
        self.mock(runner, 'BUILD_MAP_SHA', new=runner.map_digest(sources))
        image = {'path': str(self.image), 'device': 1, 'inode': 2, 'size': 64,
                 'uid': os.getuid(), 'mode': 0o500, 'sha256': 'literal-image'}
        built = {key: image[key] for key in ('path', 'device', 'inode', 'size', 'sha256')}
        built['executed'] = False
        report = {'passed': True, 'mode': '--provider-callback-build', 'sourceHashes': sources,
                  'commands': [{'name': name, 'exit': 0} for name in [
                      'provider-callback-profile-controls', 'provider-callback-build',
                      'list-webkit-callback-capi-controls', 'list-owned-signal-lifecycle-controls']],
                  'providerCallbackBuild': {'compiledImages': {runner.IMAGE_NAME: built}}}
        for mutation in ('passed', 'sources', 'exit', 'inode', 'executed'):
            changed = json.loads(json.dumps(report))
            if mutation == 'passed':
                changed['passed'] = False
            elif mutation == 'sources':
                changed['sourceHashes'] = {'source': 'wrong'}
            elif mutation == 'exit':
                changed['commands'][0]['exit'] = 1
            else:
                changed['providerCallbackBuild']['compiledImages'][runner.IMAGE_NAME][mutation] = 99
            report_raw = json.dumps(changed).encode()
            packet = dict(self.packet_fixture(), image=image,
                          buildReport={'path': str(self.output / 'report.json'), 'sha256': runner.digest(report_raw)})
            packet_raw = json.dumps(packet).encode()
            helper = SimpleNamespace(SYSTEM_SHA='fixture-sdk', unique=dict,
                                     regular=Mock(side_effect=[packet_raw, report_raw]))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                runner.read_packet(helper, runner.digest(packet_raw))
        self.spawn.assert_not_called()

    def test_kill_denial_retains_failed_execution_receipt(self):
        self.chunks[11] = [b'x' * 65537]
        self.kill.side_effect = PermissionError('owned-group kill denied')
        outcome, _, _ = runner.collect(self.image, self.output, runner.sample_budget())
        self.assertFalse(outcome['passed'])
        self.assertTrue(outcome['cleanupUnknown'])
        self.assertIn('killError', outcome)


if __name__ == "__main__":
    unittest.main()

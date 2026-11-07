"""Literal safety controls; no compositor, input or native executable runs."""
import copy
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("journey", Path(__file__).with_name("run_ux003_native_journey.py"))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("journey module unavailable")
journey = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(journey)


class JourneyControls(unittest.TestCase):
    def test_literal_recorder_bytes(self):
        self.assertEqual(journey.ARGV_BYTES, b'["two words","","caf\\233"]\n')
        self.assertFalse(journey.argv_matches(b'["two words","","caf\\56515\\56489"]\n', b""))
        self.assertTrue(journey.argv_matches(b'["two words","","caf\\233"]\n', b""))
        self.assertFalse(journey.argv_matches(journey.ARGV_BYTES, b"warning"))

    def test_environment_never_inherits_host_input_or_loader(self):
        result = journey.product_environment({"XDG_RUNTIME_DIR": "/private", "WAYLAND_DISPLAY": "/private/socket", "DBUS_SESSION_BUS_ADDRESS": "unix:path=/private/bus", "DISPLAY": ":0", "WAYLAND_SOCKET": "4", "LD_PRELOAD": "evil", "LD_LIBRARY_PATH": "/other", "GLIBC_TUNABLES": "evil", "PATH": "/bad", "HOME": "/host"})
        for key in ("DISPLAY", "WAYLAND_SOCKET", "LD_PRELOAD", "LD_LIBRARY_PATH", "GLIBC_TUNABLES", "HOME"):
            self.assertNotIn(key, result)
        self.assertEqual(result["WAYLAND_DISPLAY"], "/private/socket")
        self.assertEqual(result["LANG"], "C.UTF-8")

    def test_foreign_display_rejected(self):
        for env in ({}, {"XDG_RUNTIME_DIR": "/private", "WAYLAND_DISPLAY": "wayland-0"}, {"XDG_RUNTIME_DIR": "/private", "WAYLAND_DISPLAY": "/host/socket"}):
            with self.assertRaises(ValueError):
                journey.product_environment(env)

    def test_original_deadline_no_refresh(self):
        clock = {"origin": 100, "deadline": 200, "last": 100, "boot": "a"}
        self.assertEqual(journey.remaining(clock, 150, "a"), 50)
        self.assertEqual(clock["deadline"], 200)
        for now, boot in ((149, "a"), (200, "a"), (160, "b")):
            with self.assertRaises((ValueError, TimeoutError)):
                journey.remaining(dict(clock), now, boot)

    def test_no_unknown_input_step(self):
        with self.assertRaises(ValueError):
            journey.pointer_input("foreign", (20, 30), (980, 680))
        for point in ((-1, 2), (980, 2), (1, 680), (True, 1)):
            with self.assertRaises(ValueError):
                journey.pointer_input("open", point, (980, 680))
        self.assertEqual(journey.pointer_input("open", (20, 30), (980, 680)), b"move 20 30\nbutton 272 1\nbutton 272 0\n")

    def test_only_fixed_keyboard_arguments(self):
        self.assertEqual(journey.keyboard_args("search"), ["Owned Recorder"])
        self.assertEqual(journey.keyboard_args("close"), ["-M", "alt", "-k", "F4", "-m", "alt"])
        with self.assertRaises(ValueError):
            journey.keyboard_args("exec")

    def test_unarmed_packet_cannot_start(self):
        for packet in ({}, {"schema": 1, "kind": "fixed-ux003-native-journey", "armed": False}, {"schema": 1, "kind": "fixed-ux003-native-journey", "armed": True}):
            with self.assertRaises(ValueError):
                journey.packet_shape(packet)

    def test_missing_receipt_cannot_pass(self):
        for row in ({}, {"application": None}, {"application": {"stdoutHex": journey.ARGV_BYTES.hex(), "stderrHex": "", "exit": 1, "custody": "Available"}}):
            self.assertFalse(journey.observation_checks(row)["literalArgv"])

    def test_partial_is_not_native_acceptance(self):
        row = {"application": {"stdoutHex": journey.ARGV_BYTES.hex(), "stderrHex": "", "exit": 0, "custody": "Available", "containment": "BeforeSignalLeaderExited"}, "backend": {"passed": True, "cleanup": True}, "owner": {"passed": True, "cleanup": True, "engineCleanup": True}}
        checks = journey.observation_checks(row)
        self.assertTrue(checks["literalArgv"])
        self.assertTrue(checks["reportedOwnerCleanup"])
        self.assertFalse(checks["fullJourneyAccepted"])
        self.assertIsNone(checks["catalogRevision"])
        self.assertIn("catalog revision and eligible/hidden rendered entries", checks["missingObservations"])

    def test_boolean_exit_is_not_normal_exit(self):
        row = {"application": {"stdoutHex": journey.ARGV_BYTES.hex(), "stderrHex": "", "exit": False, "custody": "Available", "containment": "BeforeSignalLeaderExited"}}
        self.assertFalse(journey.observation_checks(row)["literalArgv"])

    def test_owner_cleanup_not_inferred_from_backend_exit(self):
        row = {"backend": {"passed": True, "cleanup": True}, "owner": {"passed": True, "engineCleanup": False}}
        self.assertFalse(journey.observation_checks(row)["reportedOwnerCleanup"])

    def test_invalid_hex_fails_closed(self):
        row = {"application": {"stdoutHex": "nothex", "stderrHex": "", "exit": 0, "custody": "Available", "containment": "BeforeSignalLeaderExited"}}
        self.assertFalse(journey.observation_checks(row)["literalArgv"])

    def test_oversized_or_extra_observer_output_refused(self):
        for raw in (b"x" * (journey.LOG_LIMIT + 1), b"{}\n{}\n", b"{\"x\":1,\"x\":2}\n"):
            with self.assertRaises(ValueError):
                journey.decode_observation(raw)

    def test_hidden_search_is_fixed_and_cleared(self):
        self.assertEqual(journey.keyboard_args("hidden-search"), ["Hidden Recorder"])
        self.assertEqual(journey.keyboard_args("clear-search"), ["-M", "ctrl", "-k", "a", "-m", "ctrl", "-k", "BackSpace"])

    def complete_diagnostic(self):
        return {
          "backend": {"passed": True, "cleanup": True},
          "application": {"request": "11", "stdoutHex": journey.ARGV_BYTES.hex(), "stderrHex": "", "exit": 0, "custody": "Available", "containment": "BeforeSignalLeaderExited"},
          "publishedLaunch": {"request": "11", "lifetime": "9007199254740993", "generation": "1", "entry": "ux003-recorder",
            "catalog": {"protocolVersion": 3, "kind": "application-catalog", "binding": {"lifetime": "9007199254740993", "session": "9007199254740995", "frontend": "9007199254740997"},
              "snapshot": {"catalogProtocol": 2, "lifetime": "9007199254740993", "generation": "1", "entries": [{"id": "ux003-recorder", "name": "Owned Recorder"}]}}},
          "owner": {"passed": True, "cleanup": True, "engineCleanup": True,
            "engineObservation": {"kind": "owned-engine-terminal-observation", "authority": False, "incarnation": "100", "deadlineMonotonicNs": "500",
              "guiObservation": {"controllerLoaded": True, "barLoaded": True, "popupLoaded": True, "mvpAttached": True, "loopReturned": True, "callbackCustody": "process-pinned"},
              "brokerTerminal": "GuiObservationWrittenLocally", "brokerClose": "CloseConfirmed",
              "engine": {"pid": "200", "startTicks": "90", "originalDeadline": "500", "normalExit": True, "reaped": True, "ownedReceiptMatches": True, "disposition": "EngineExitedNormally", "waitStatus": ["1", "0"], "lastLiveImage": {"digestSampleMonotonicNs": "110", "checkedMonotonicNs": "120"}},
              "backing": {"path": "/tmp/warlock-ui-backing-" + "a" * 64, "device": "1", "inode": "2", "owner": "1000", "retired": True}}}}

    def test_exact_actual_catalog_and_parent_receipts_are_observable(self):
        checks = journey.observation_checks(self.complete_diagnostic())
        self.assertEqual(checks["catalogRevision"], "1")
        self.assertTrue(checks["catalogLaunchBound"])
        self.assertTrue(checks["typedParentCompletion"])
        self.assertTrue(checks["journeyFactsObserved"])
        self.assertFalse(checks["fullJourneyAccepted"])

    def test_foreign_revision_hidden_entry_and_wrong_request_refuse(self):
        for key, value in (("generation", "2"), ("lifetime", "1"), ("request", "12"), ("entry", "ux003-hidden")):
            row = self.complete_diagnostic(); row["publishedLaunch"][key] = value
            self.assertFalse(journey.observation_checks(row)["catalogLaunchBound"])
        row = self.complete_diagnostic()
        row["publishedLaunch"]["catalog"]["snapshot"]["entries"].append({"id": "ux003-hidden", "name": "Hidden Recorder"})
        self.assertFalse(journey.observation_checks(row)["catalogLaunchBound"])

    def test_unknown_forced_mismatched_or_incomplete_parent_never_complete(self):
        row = self.complete_diagnostic()
        for branch, key, value in (("engine", "normalExit", False), ("engine", "reaped", False), ("engine", "ownedReceiptMatches", False), ("engine", "disposition", "EngineForcedFallback"), ("engine", "originalDeadline", "501"), ("engine", "lastLiveImage", None), ("backing", "retired", False), ("guiObservation", "popupLoaded", False)):
            bad = copy.deepcopy(row); bad["owner"]["engineObservation"][branch][key] = value
            self.assertFalse(journey.observation_checks(bad)["typedParentCompletion"])
        for key, value in (("brokerTerminal", "ReplyWrittenLocally"), ("brokerClose", "CloseUnknown"), ("authority", True)):
            bad = copy.deepcopy(row); bad["owner"]["engineObservation"][key] = value
            self.assertFalse(journey.observation_checks(bad)["typedParentCompletion"])

    def build_binding(self):
        names = ['implementation/warlock/haskell/runtime/src/Warlock/Backend.hs',
                 'implementation/warlock/haskell/runtime/ui/Main.hs',
                 'implementation/warlock/haskell/runtime/fixture-ux003-native-observer/Main.hs']
        sources = dict.fromkeys(names, 'a' * 64)
        assets = {role: {'path': '/private/' + role, 'sha256': 'b' * 64} for role in ('owner', 'observer')}
        images = {name: dict(assets[role], device='58', inode='7', size='4096', executed=False)
                  for role, name in (('owner', 'warlock-ui-owner'), ('observer', 'ux003-native-observer'))}
        packet = {'assets': assets, 'sourceHashes': sources}
        build = {'passed': True, 'sourceHashes': sources.copy(), 'physicalContextBuild': {
            'targets': ['warlock-runtime:exe:warlock-ui-owner', 'warlock-runtime:exe:ux003-native-observer'],
            'compiledImages': images}}
        return packet, build

    def test_build_binds_two_actual_images_and_source_closure(self):
        packet, build = self.build_binding()
        pins = journey.build_asset_bindings(packet, build)
        self.assertEqual(set(pins), {'owner', 'observer'})
        self.assertEqual(pins['observer']['path'], '/private/observer')

    def test_passed_without_actual_compilation_cannot_qualify_assets(self):
        packet, build = self.build_binding()
        for field in ('compiledImages', 'targets'):
            wrong = copy.deepcopy(build); wrong['physicalContextBuild'][field] = {} if field == 'compiledImages' else []
            with self.assertRaises(ValueError): journey.build_asset_bindings(packet, wrong)
        for key, value in (('path', '/foreign/image'), ('sha256', 'c' * 64), ('size', '0'), ('inode', '-1')):
            wrong = copy.deepcopy(build); wrong['physicalContextBuild']['compiledImages']['ux003-native-observer'][key] = value
            with self.assertRaises(ValueError): journey.build_asset_bindings(packet, wrong)
        wrong = copy.deepcopy(build); wrong['sourceHashes']['unbound/source.hs'] = 'a' * 64
        with self.assertRaises(ValueError): journey.build_asset_bindings(packet, wrong)
        wrong = copy.deepcopy(build); wrong['sourceHashes'][next(iter(wrong['sourceHashes']))] = 'd' * 64
        with self.assertRaises(ValueError): journey.build_asset_bindings(packet, wrong)


if __name__ == "__main__":
    unittest.main()

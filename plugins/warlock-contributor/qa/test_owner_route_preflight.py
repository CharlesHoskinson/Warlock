"""Literal binding regression; no runner or protected child is executed."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/owner_route_preflight.py'
spec = importlib.util.spec_from_file_location('owner_route_preflight', SCRIPT)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)

TARGETS = (
    ('application-owner-peer-fixture', 'executable', 'fixture-application-owner-peer'),
    ('application-argv-fixture', 'executable', 'fixture-application-argv'),
    ('application-owner-route-controls', 'test-suite', 'test-application-owner-route'),
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def runner(pins):
    return ("def main():\n if args.application_owner_route:\n"
            f"  application_targets = {TARGETS!r}\n"
            "  for name, kind, directory in application_targets:\n"
            "   directory_root = stage / 'runtime' / directory\n"
            f"   if digest(directory_root / 'Main.hs') != {pins!r}[name]:\n"
            "    raise RuntimeError('source pin differs')\n").encode()


class OwnerRoutePreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bodies = {name: (name + '\n').encode() for name, _, _ in TARGETS}
        self.pins = {name: digest(body) for name, body in self.bodies.items()}
        self.paths = {}
        for name, _, directory in TARGETS:
            path = 'implementation/warlock/haskell/runtime/' + directory + '/Main.hs'
            self.paths[name] = path
            target = self.root / path
            target.parent.mkdir(parents=True)
            target.write_bytes(self.bodies[name])

    def packet(self, source=None, mode='--application-owner-route'):
        source = runner(self.pins) if source is None else source
        target = self.root / 'tools/check_arm64_cpu.py'
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(source)
        packet = {'schema': 1, 'runner': str(target), 'arguments': [mode],
                  'inputs': {'tools/check_arm64_cpu.py': digest(source),
                             **{path: digest((self.root / path).read_bytes())
                                for path in self.paths.values()}}}
        data = (json.dumps(packet, sort_keys=True) + '\n').encode()
        (self.root / 'review.json').write_bytes(data)
        return digest(data)

    def inspect(self, expected=None):
        expected = self.packet() if expected is None else expected
        return preflight.inspect(self.root, 'review.json', expected)

    def test_packet_hashes_correct_but_embedded_old_fixture_refused(self):
        pins = dict(self.pins, **{'application-owner-route-controls': digest(b'old fixture\n')})
        expected = self.packet(runner(pins))
        with self.assertRaisesRegex(preflight.Refused, 'Embedded fixture pin differs'):
            self.inspect(expected)

    def test_consistent_bindings_are_advisory_only(self):
        result = self.inspect()
        self.assertEqual(len(result['fixtureBindings']), 3)
        self.assertEqual(result['status'], 'consistent-advisory-only')
        self.assertFalse(result['sourceReady'])
        self.assertFalse(result['nativeAuthority'])
        self.assertTrue(result['fullQaAndAllOtherGuardsStillRequired'])

    def test_packet_sha_is_not_optional(self):
        self.packet()
        with self.assertRaisesRegex(preflight.Refused, 'Review digest'):
            self.inspect('0' * 64)

    def test_fixture_change_after_packet_refused(self):
        expected = self.packet()
        (self.root / self.paths['application-argv-fixture']).write_bytes(b'changed\n')
        with self.assertRaisesRegex(preflight.Refused, 'Current fixture differs'):
            self.inspect(expected)

    def test_runner_change_after_packet_refused(self):
        expected = self.packet()
        with (self.root / 'tools/check_arm64_cpu.py').open('ab') as stream:
            stream.write(b'\n# changed\n')
        with self.assertRaisesRegex(preflight.Refused, 'Current runner differs'):
            self.inspect(expected)

    def test_other_modes_are_not_approved(self):
        expected = self.packet(mode='--protocol')
        with self.assertRaisesRegex(preflight.Refused, 'Only fixed application-owner-route'):
            self.inspect(expected)

    def test_dynamic_map_refused(self):
        source = runner(self.pins).replace(repr(self.pins).encode() + b'[name]', b'PINS[name]')
        expected = self.packet(source)
        with self.assertRaisesRegex(preflight.Refused, 'literal map'):
            self.inspect(expected)

    def test_duplicate_hash_check_is_ambiguous(self):
        expected = self.packet(runner(self.pins) + runner(self.pins).replace(b'def main():', b'def other():'))
        with self.assertRaisesRegex(preflight.Refused, 'one fixed digest comparison'):
            self.inspect(expected)

    def test_duplicate_literal_key_refused(self):
        literal = repr(self.pins)
        duplicate = literal[:-1] + ', ' + repr('application-owner-route-controls') + ': ' + repr(self.pins['application-owner-route-controls']) + '}'
        expected = self.packet(runner(self.pins).replace(literal.encode(), duplicate.encode()))
        with self.assertRaisesRegex(preflight.Refused, 'unique fixed fixture keys'):
            self.inspect(expected)

    def test_dynamic_target_list_refused(self):
        expected = self.packet(runner(self.pins).replace(repr(TARGETS).encode(), b'load_targets()'))
        with self.assertRaisesRegex(preflight.Refused, 'literal target list'):
            self.inspect(expected)

    def test_symlink_fixture_refused(self):
        expected = self.packet()
        path = self.root / self.paths['application-argv-fixture']
        data = path.read_bytes()
        path.unlink()
        (self.root / 'other.hs').write_bytes(data)
        path.symlink_to(self.root / 'other.hs')
        with self.assertRaises(preflight.Refused):
            self.inspect(expected)

    def test_runner_top_level_code_never_executes(self):
        expected = self.packet(b"raise RuntimeError('runner must never execute')\n" + runner(self.pins))
        self.assertEqual(self.inspect(expected)['status'], 'consistent-advisory-only')


if __name__ == '__main__':
    unittest.main()

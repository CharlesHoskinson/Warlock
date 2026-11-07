"""Actual outer builder failure evidence; all protected effects are fixed mocks."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

FIXTURES = Path(__file__).parent / 'fixtures/native-build-failure'
REPO = Path(__file__).resolve().parents[3]
BUILDER = Path(os.environ.get('WARLOCK_FAILURE_BUILDER', REPO / 'tools/check_arm64_cpu.py'))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NativeBuildFailureEvidenceTests(unittest.TestCase):
    def run_outer(self, inner):
        with mock.patch.object(sys, 'path', [str(REPO / 'tools'), *sys.path]):
            builder = load('failure_outer_builder', BUILDER)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / '.warlock-contributor/arm64-cpu-1'

            def child(*args, **kwargs):
                report = json.loads((output / 'report.json').read_text())
                if inner is not None:
                    report['error'] = inner
                (output / 'report.json').write_text(json.dumps(report))
                return types.SimpleNamespace(returncode=1)

            with mock.patch.object(builder, 'ROOT', root), \
                 mock.patch.object(builder, 'require_qa_scope', return_value={}), \
                 mock.patch.object(builder, 'runtime_base'), \
                 mock.patch.object(builder, 'arm64_inputs', return_value=[]), \
                 mock.patch.object(builder, 'verify', return_value={'manifestSHA256': 'fixed', 'trees': [], 'files': {}}), \
                 mock.patch.object(builder.time, 'time_ns', return_value=1), \
                 mock.patch.object(builder.subprocess, 'run', side_effect=child) as process, \
                 mock.patch.object(sys, 'argv', [str(BUILDER), '--native-stage-build']), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(builder.main(), 1)
                self.assertEqual(process.call_count, 1)
            return json.loads((output / 'report.json').read_text())

    def test_actual_frozen_libc_parser_error_survives_outer_failure(self):
        helper = load('failure_frozen_helper66c', FIXTURES / 'helper66c.py')
        with self.assertRaisesRegex(ValueError, '^Unsupported or ambiguous AArch64 interpreter$') as caught:
            helper.readelf_dependencies((FIXTURES / 'libc-readelf11.stdout').read_text())
        inner = str(caught.exception)
        report = self.run_outer(inner)
        self.assertFalse(report['passed'])
        self.assertEqual(report['error'], inner)
        self.assertEqual(report['outerError'], 'Private ARM profile failed; retained logs')
        self.assertFalse(report['nativeAcceptance'])
        self.assertFalse(report['originalAcceptance'])
        self.assertFalse(report['releaseAccepted'])

    def test_missing_empty_or_malformed_inner_error_uses_outer_failure(self):
        for inner in (None, '', 7, {}, [], False):
            with self.subTest(inner=inner):
                report = self.run_outer(inner)
                self.assertFalse(report['passed'])
                self.assertEqual(report['error'], 'Private ARM profile failed; retained logs')
                self.assertNotIn('outerError', report)


if __name__ == '__main__':
    unittest.main()

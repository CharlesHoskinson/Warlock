"""Offline receipt normalization controls; never invoke workflow or product QA."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/canonicalize_review.py'
helper: ModuleType | None = None
if SCRIPT.is_file():
    spec = importlib.util.spec_from_file_location('canonicalize_review', SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError('Review helper module loader unavailable')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        if helper is None:
            self.fail('canonical review receipt helper is missing')
        assert helper is not None
        self.module: ModuleType = helper
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'original.json'
        self.output = self.root / 'canonical.json'
        self.receipt = {'schema': 1, 'reviewer': 'independent-peer', 'scope': 'cpu',
                        'candidateSha256': 'a' * 64, 'verdict': 'accepted',
                        'findings': [], 'limits': ['source readiness only'],
                        'checks': {'fixedSources': True}}
        self.write(self.receipt)

    def write(self, receipt):
        self.source.write_text(json.dumps(receipt) + '\n', encoding='utf-8')

    def arguments(self, **changes):
        args = {'input_path': str(self.source),
                'expected_sha256': hashlib.sha256(self.source.read_bytes()).hexdigest(),
                'candidate_sha256': 'a' * 64, 'reviewer': 'independent-peer',
                'owner': 'root-owner', 'scope': 'cpu', 'output_path': str(self.output)}
        args.update(changes)
        return args

    def normalize(self, **changes):
        return self.module.canonicalize(**self.arguments(**changes))

    def refuse(self, **changes):
        with self.assertRaises((ValueError, OSError)):
            self.normalize(**changes)
        self.assertFalse(self.output.exists())

    def test_verdict_becomes_disposition_without_rewriting_decision_or_source(self):
        before = self.source.read_bytes()
        result = self.normalize()
        written = json.loads(self.output.read_text())
        self.assertEqual(result, written)
        for key, value in self.receipt.items():
            self.assertEqual(written[key], value)
        self.assertEqual(written['disposition'], 'accepted')
        self.assertEqual(written['receiptCanonicalization']['original'],
                         {'path': str(self.source), 'sha256': hashlib.sha256(before).hexdigest()})
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o600)
        self.assertEqual({p.name for p in self.root.iterdir()}, {'original.json', 'canonical.json'})

    def test_changes_required_is_never_promoted(self):
        self.receipt['verdict'] = 'changes-required'
        self.write(self.receipt)
        self.assertEqual(self.normalize()['disposition'], 'changes-required')

    def test_existing_disposition_and_matching_alias_preserved(self):
        for alias in [False, True]:
            with self.subTest(alias=alias):
                receipt = dict(self.receipt, disposition='accepted')
                if not alias:
                    del receipt['verdict']
                self.write(receipt)
                self.assertEqual(self.normalize()['disposition'], 'accepted')
                self.output.unlink()

    def test_conflicting_decisions_refused(self):
        self.write(dict(self.receipt, disposition='changes-required'))
        self.refuse()

    def test_invalid_alias_never_hidden_by_valid_disposition(self):
        for value in ['approve', 'Accepted', ' accepted', True, None, {'accepted': True}]:
            with self.subTest(value=value):
                self.write(dict(self.receipt, verdict=value, disposition='accepted'))
                self.refuse()

    def test_missing_decision_refused(self):
        receipt = dict(self.receipt)
        del receipt['verdict']
        self.write(receipt)
        self.refuse()

    def test_each_required_identity_field_must_be_present(self):
        for key in ['candidateSha256', 'reviewer', 'scope', 'schema']:
            with self.subTest(key=key):
                receipt = dict(self.receipt)
                del receipt[key]
                self.write(receipt)
                self.refuse()

    def test_wrong_candidate_reviewer_scope_and_schema_refused(self):
        for key, value in [('candidateSha256', 'b' * 64), ('reviewer', 'another-peer'),
                           ('scope', 'native'), ('schema', True), ('schema', 2)]:
            with self.subTest(key=key):
                self.write(dict(self.receipt, **{key: value}))
                self.refuse()

    def test_self_review_refused_case_insensitively(self):
        self.refuse(owner='INDEPENDENT-PEER')

    def test_expected_identity_values_validated(self):
        for args in [{'candidate_sha256': 'A' * 64}, {'candidate_sha256': 'a'},
                     {'reviewer': ''}, {'reviewer': 'independent-peer\n'},
                     {'owner': ' root-owner'}, {'scope': 'all'}, {'expected_sha256': 'f' * 64}]:
            with self.subTest(args=args):
                self.refuse(**args)

    def test_malformed_and_duplicate_json_refused(self):
        for raw in [b'[]', b'{', b'{"schema":1,"schema":1}',
                    b'{"checks":{"same":true,"same":false}}', b'{"value":NaN}', b'\xff']:
            with self.subTest(raw=raw):
                self.source.write_bytes(raw)
                self.refuse()

    def test_existing_canonicalization_metadata_not_overwritten(self):
        self.write(dict(self.receipt, receiptCanonicalization={'original': 'untrusted'}))
        self.refuse()

    def test_receipt_size_bound(self):
        self.source.write_bytes(b' ' * (1048576 + 1))
        self.refuse()

    def test_input_symlink_refused(self):
        link = self.root / 'input-link.json'
        link.symlink_to(self.source)
        self.refuse(input_path=str(link))

    def test_input_parent_symlink_refused(self):
        real = self.root / 'real'
        real.mkdir()
        nested = real / 'source.json'
        nested.write_bytes(self.source.read_bytes())
        alias = self.root / 'alias'
        alias.symlink_to(real, target_is_directory=True)
        self.refuse(input_path=str(alias / 'source.json'))

    def test_output_parent_symlink_refused(self):
        real = self.root / 'real'
        real.mkdir()
        alias = self.root / 'alias'
        alias.symlink_to(real, target_is_directory=True)
        self.refuse(output_path=str(alias / 'new.json'))
        self.assertFalse((real / 'new.json').exists())

    def test_relative_and_parent_traversal_paths_refused(self):
        self.refuse(input_path='original.json')
        self.refuse(output_path='canonical.json')
        self.refuse(input_path=str(self.root) + '/../' + self.root.name + '/original.json')
        self.refuse(output_path=str(self.root) + '/./canonical.json')

    def test_existing_output_never_overwritten(self):
        self.output.write_bytes(b'existing evidence')
        with self.assertRaises((ValueError, OSError)):
            self.normalize()
        self.assertEqual(self.output.read_bytes(), b'existing evidence')
        self.assertFalse(any(p.name.startswith('.review-') for p in self.root.iterdir()))

    def test_output_symlink_and_hardlink_never_overwritten(self):
        original = self.source.read_bytes()
        for kind in ['symlink', 'hardlink', 'dangling']:
            with self.subTest(kind=kind):
                if kind == 'hardlink':
                    os.link(self.source, self.output)
                else:
                    self.output.symlink_to(self.source if kind == 'symlink' else self.root / 'absent')
                with self.assertRaises((ValueError, OSError)):
                    self.normalize()
                self.assertEqual(self.source.read_bytes(), original)
                self.output.unlink()

    def test_input_output_same_path_refused(self):
        original = self.source.read_bytes()
        with self.assertRaises((ValueError, OSError)):
            self.normalize(output_path=str(self.source))
        self.assertEqual(self.source.read_bytes(), original)

    def test_nonregular_input_refused_without_opening_fifo_for_io(self):
        fifo = self.root / 'fifo'
        os.mkfifo(fifo)
        self.refuse(input_path=str(fifo))
        self.refuse(input_path=str(self.root))

    def test_group_writable_output_parent_refused(self):
        self.root.chmod(0o770)
        self.addCleanup(self.root.chmod, 0o700)
        self.refuse()
        self.assertFalse(any(p.name.startswith('.review-') for p in self.root.iterdir()))

    def test_world_writable_output_parent_refused_even_when_sticky(self):
        self.root.chmod(0o1777)
        self.addCleanup(self.root.chmod, 0o700)
        self.refuse()

    def test_unsafe_ancestor_refused_with_private_leaf_parent(self):
        ancestor = self.root / 'unsafe'
        parent = ancestor / 'private'
        parent.mkdir(parents=True, mode=0o700)
        target = parent / 'result.json'
        self.addCleanup(ancestor.chmod, 0o700)
        for mode in [0o770, 0o777]:
            with self.subTest(mode=mode):
                ancestor.chmod(mode)
                with self.assertRaises((ValueError, OSError)):
                    self.normalize(output_path=str(target))
                self.assertFalse(target.exists())
                self.assertFalse(list(parent.iterdir()))

    def test_private_nested_output_parent_allowed(self):
        parent = self.root / 'private' / 'nested'
        parent.mkdir(parents=True, mode=0o700)
        output = parent / 'canonical.json'
        self.normalize(output_path=str(output))
        self.assertEqual(json.loads(output.read_text())['disposition'], 'accepted')

    def test_valid_native_scope_stays_native(self):
        self.write(dict(self.receipt, scope='native'))
        self.assertEqual(self.normalize(scope='native')['scope'], 'native')

    def test_cli_requires_context_and_reports_written_hash(self):
        args = self.arguments()
        argv = ['--input', args['input_path'], '--sha256', args['expected_sha256'],
                '--candidate-sha256', args['candidate_sha256'], '--reviewer', args['reviewer'],
                '--owner', args['owner'], '--scope', args['scope'], '--output', args['output_path']]
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(self.module.main(argv), 0)
        result = json.loads(stdout.getvalue())
        self.assertEqual(result['sha256'], hashlib.sha256(self.output.read_bytes()).hexdigest())
        self.assertEqual(result['path'], str(self.output))
        self.assertFalse(result['acceptanceAuthority'])
        self.assertEqual(result['disposition'], 'accepted')
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.module.main(argv), 1)


if __name__ == '__main__':
    unittest.main()

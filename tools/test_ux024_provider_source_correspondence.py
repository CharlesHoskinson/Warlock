#!/usr/bin/env python3
"""Fixed source-correspondence controls. No provider/native execution."""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

parser = argparse.ArgumentParser()
parser.add_argument('--module', required=True)
parser.add_argument('--runner', required=True)
parser.add_argument('--historical-source', required=True)
parser.add_argument('--current-source', required=True)
args, rest = parser.parse_known_args()
spec = importlib.util.spec_from_file_location('fixed_provider_correspondence', args.module)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
OLD = '02e1739d85a75210b70702ed269d11a84c498755e8fc0b567bfe42492a656804'
NEW = 'efbd361b826826d9a87681ec9cfcd8ce3ed4b0779d6bf52702f2329eb53e10d8'
ROOT = Path('/home/hoskinson/Projects/Warlock')


class Controls(unittest.TestCase):
    def setup_proof(self):
        self.old = Path(args.historical_source).read_bytes()
        self.new = Path(args.current_source).read_bytes()
        self.assertEqual(hashlib.sha256(self.old).hexdigest(), OLD)
        self.assertEqual(hashlib.sha256(self.new).hexdigest(), NEW)
        self.report = {'path': '/fixed/retained-report.json', 'sha256': 'e9ced42313e67a46c1e5f9fa0058b6661b82d2ef3c47ab81925815a9acf23938'}
        self.proof = dict(schema=1, disposition='accepted', scope='ux024-provider-qa-dispatch-source-correspondence', reviewer='build_audit', buildReport=self.report,
                          historicalSource={'path': '/fixed/old.py', 'sha256': OLD}, currentSource={'path': str(ROOT/'tools/qa_cpu.py'), 'sha256': NEW},
                          correspondenceEvidence={'path': '/fixed/evidence.json', 'sha256': 'b'*64})
        self.reference = {'path': '/fixed/proof.json', 'sha256': 'a'*64}
        self.reads = []
        def pinned(ref, cap):
            self.reads.append(ref)
            return {'/fixed/proof.json': json.dumps(self.proof).encode(), '/fixed/old.py': self.old,
                    str(ROOT/'tools/qa_cpu.py'): self.new, '/fixed/evidence.json': b'{}'}[ref['path']]
        self.current = SimpleNamespace(pinned=pinned)

    def test_exact_historical_and_current_full_source_correspond(self):
        self.setup_proof()
        self.assertEqual(m.provider_source_pin(self.current, self.reference, self.report, Path('tools/qa_cpu.py'), OLD), NEW)
        self.assertIn(self.proof['historicalSource'], self.reads)
        self.assertIn(self.proof['currentSource'], self.reads)

    def test_default_and_other_paths_keep_exact_historical_hash(self):
        self.setup_proof()
        self.assertEqual(m.provider_source_pin(self.current, None, self.report, Path('tools/qa_cpu.py'), OLD), OLD)
        self.assertEqual(m.provider_source_pin(self.current, self.reference, self.report, Path('tools/aquamarine_build.py'), 'c'*64), 'c'*64)
        self.assertEqual(self.reads, [])

    def test_wrong_report_source_hash_path_scope_and_author_refuse(self):
        self.setup_proof()
        original = copy.deepcopy(self.proof)
        for field, value in [('disposition', 'pending'), ('scope', 'generic'), ('reviewer', 'Root'), ('reviewer', 'sol_supervisor'), ('reviewer', 'arbitrary'),
                             ('buildReport', dict(self.report, sha256='0'*64)),
                             ('historicalSource', {'path': '/fixed/old.py', 'sha256': '0'*64}),
                             ('currentSource', {'path': str(ROOT/'tools/aquamarine_build.py'), 'sha256': NEW})]:
            self.proof = dict(original, **{field: value})
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.provider_source_pin(self.current, self.reference, self.report, Path('tools/qa_cpu.py'), OLD)
        self.proof = original
        with self.assertRaises(ValueError):
            m.provider_source_pin(self.current, self.reference, self.report, Path('tools/qa_cpu.py'), '0'*64)

    def test_actual_bytes_not_precomputed_pass_booleans(self):
        self.setup_proof()
        self.old += b'\n# changed\n'
        self.proof['passed'] = True
        with self.assertRaises(ValueError):
            m.provider_source_pin(self.current, self.reference, self.report, Path('tools/qa_cpu.py'), OLD)

    def test_provider_branch_or_budget_mutation_rejected_by_ast(self):
        self.setup_proof()
        for old, new in [(b'def arm64_inputs(', b'def changed_arm64_inputs('),
                         (b'3600 if haskell or arm64 or team_quint', b'3601 if haskell or arm64 or team_quint')]:
            self.assertIn(old, self.new)
            with self.subTest(mutation=old), self.assertRaises(ValueError):
                m.provider_qa_ast_correspondence(self.old, self.new.replace(old, new, 1))

    def test_correspondence_does_not_skip_regular_verification(self):
        tree = ast.parse(Path(args.module).read_text())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'verify_private_provider')
        calls = [n for n in ast.walk(function) if isinstance(n, ast.Call)]
        self.assertTrue(any(isinstance(n.func, ast.Attribute) and n.func.attr == 'regular' and
                            any(isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id == 'provider_source_pin' for arg in n.args) for n in calls))
        self.assertIn("for name, pin_sha in report['sourceInputs'].items():", ast.get_source_segment(Path(args.module).read_text(), function))
        self.assertIn('base.private_soname', ast.get_source_segment(Path(args.module).read_text(), function))

    def test_explicit_propagation_preflight_start_and_generated_recheck(self):
        source = Path(args.runner).read_text()
        tree = ast.parse(source)
        direct = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'verify_private_provider']
        mapped = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'generated_context_mapped']
        self.assertEqual(len(direct), 2)
        self.assertTrue(all(len(n.args) == 5 for n in direct))
        self.assertEqual(len(mapped), 2)
        self.assertTrue(all(len(n.args) == 12 for n in mapped))
        helper = ast.parse(Path(args.module).read_text())
        generated = next(n for n in helper.body if isinstance(n, ast.FunctionDef) and n.name == 'generated_context_mapped')
        forwarded = [n for n in ast.walk(generated) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'verify_private_provider']
        self.assertEqual(len(forwarded), 1)
        self.assertEqual(ast.dump(forwarded[0].args[-1]), "Name(id='source_correspondence', ctx=Load())")

    def test_new_namespace_preserves_old_native_packet(self):
        tree = ast.parse(Path(args.runner).read_text())
        packet = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PACKET' for t in n.targets))
        self.assertIn('ux024-connected-foreign-toplevel-observer-v2/packet.json', ast.unparse(packet))


if __name__ == '__main__':
    unittest.main(argv=[__file__, *rest])

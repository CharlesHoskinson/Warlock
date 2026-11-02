#!/usr/bin/env python3
"""Source-bound graph contracts; run with the installed Graphify interpreter.

All graph writes are confined to a temporary fixture. No production index or
GPU model is needed. This is retrieval QA, not Quint or EARS verification.
"""
import json
from pathlib import Path
import random
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import warlock_ctx as ctx
import warlock_gpu as gpu


SOURCE = Path(__file__).resolve().parent.parent
MODEL = 'implementation/warlock/haskell/runtime/formal/ui-origin.qnt'
MODEL_TEST = 'implementation/warlock/haskell/runtime/formal/ui-origin_test.qnt'
REGISTER = 'docs/elm-roadmap/requirements.json'
SLICE = '.warlock-contributor/ui-origin.json'
STATE = 'docs/warlock-build-loop/v2/STATE.json'
SEED = 20261101


class QuintGraphContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='warlock-graph-contract-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in (MODEL, MODEL_TEST, REGISTER, SLICE, 'tools/warlock_ctx.py'):
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / name, dest)
        state = self.root / STATE
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps({'activeContributorRecord': SLICE}))
        self.graph = self.root / 'graph/graph.json'
        self.patches = [patch.object(ctx, 'ROOT', self.root),
                        patch.object(ctx, 'CACHE', self.graph.parent),
                        patch.object(ctx, 'GRAPH', self.graph),
                        patch.object(gpu, 'ROOT', self.root),
                        patch.object(gpu, 'GRAPH', self.graph)]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)

    def publish(self):
        ctx.update()
        return json.loads(self.graph.read_bytes())

    def assert_current(self):
        self.assertEqual(ctx.load()[3], [])
        gpu.graph()

    def assert_stale(self, paths):
        self.assertTrue(set(paths).issubset(set(ctx.load()[3])))
        with self.assertRaises(RuntimeError):
            gpu.graph()

    def test_actual_register_models_and_import_candidates(self):
        graph = self.publish()
        nodes = {n['id']: n for n in graph['nodes']}
        edges = graph['links']
        kinds = [n.get('kind') for n in nodes.values()]
        self.assertEqual(kinds.count('requirement'), 242)
        self.assertEqual(kinds.count('scenario'), 417)
        self.assertIn('file:' + MODEL, nodes)
        self.assertIn('file:' + MODEL_TEST, nodes)
        self.assertTrue(any(n.get('source_file') == MODEL and n.get('label') == 'ui_origin'
                            and n.get('kind') == 'module' for n in nodes.values()))
        self.assertTrue(any(n.get('source_file') == MODEL_TEST and n.get('label') == 'controllerCommit'
                            and n.get('kind') == 'declaration' for n in nodes.values()))
        import_nodes = {n['id'] for n in nodes.values()
                        if n.get('source_file') == MODEL_TEST and n.get('kind') == 'import'
                        and 'ui_origin.*' in n.get('label', '')}
        self.assertTrue(import_nodes)
        self.assertTrue(any(e['source'] in import_nodes and e['target'] == 'file:' + MODEL
                            and e.get('relation') == 'lexical_import_path_candidate' for e in edges))
        self.assertFalse(any(e['source'] in import_nodes and e.get('relation') == 'lexical_import'
                             for e in edges))
        self.assert_current()

    def test_unresolved_and_ambiguous_names_do_not_fabricate_resolution(self):
        directory = self.root / 'implementation/warlock/qa'
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'left.qnt').write_text('module repeated {\n  val ok = true\n}\n')
        (directory / 'right.qnt').write_text('module repeated {\n  val ok = false\n}\n')
        (directory / 'probe.qnt').write_text(
            'module probe {\n import repeated.* from "./missing"\n'
            ' import repeated.* from "./left"\n}\n')
        graph = self.publish()
        nodes = {n['id']: n for n in graph['nodes']}
        imports = [n for n in nodes.values() if n.get('kind') == 'import'
                   and n.get('source_file', '').endswith('/probe.qnt')]
        self.assertEqual(len(imports), 2)
        by_label = {n['label']: n['id'] for n in imports}
        missing = by_label['import repeated.* from "./missing"']
        left = by_label['import repeated.* from "./left"']
        outgoing = [e for e in graph['links'] if e['source'] in (missing, left)]
        self.assertFalse(any(e['source'] == missing for e in outgoing))
        self.assertEqual([(e['target'], e['relation']) for e in outgoing if e['source'] == left],
                         [('file:implementation/warlock/qa/left.qnt', 'lexical_import_path_candidate')])

    def test_seeded_inventory_add_edit_remove_and_restore(self):
        self.publish()
        self.assert_current()
        rng = random.Random(SEED)
        directory = self.root / 'implementation/warlock/qa/generated'
        directory.mkdir(parents=True, exist_ok=True)
        names = ['case_%08x.qnt' % rng.getrandbits(32) for _ in range(24)]
        self.assertEqual(len(set(names)), len(names), 'seed %d' % SEED)
        paths = ['implementation/warlock/qa/generated/' + n for n in names]
        for index, name in enumerate(names):
            (directory / name).write_text('module generated_%d {\n val v = %d\n}\n' % (index, index))
        self.assert_stale(paths)
        self.publish()
        self.assert_current()
        changed = directory / names[0]
        original = changed.read_bytes()
        changed.write_bytes(original + b'// changed\n')
        self.assert_stale([paths[0]])
        changed.write_bytes(original)
        self.assert_current()
        removed = directory / names[1]
        removed_bytes = removed.read_bytes()
        removed.unlink()
        self.assert_stale([paths[1]])
        removed.write_bytes(removed_bytes)
        self.assert_current()
        for name in names:
            (directory / name).unlink()
        self.assert_stale(paths)
        self.publish()
        self.assert_current()

    def test_active_record_change_requires_fresh_graph(self):
        self.publish()
        self.assert_current()
        alternate = '.warlock-contributor/alternate.json'
        shutil.copyfile(self.root / SLICE, self.root / alternate)
        (self.root / STATE).write_text(json.dumps({'activeContributorRecord': alternate}))
        self.assert_stale([STATE])
        graph = self.publish()
        self.assertIn(alternate, graph['graph']['input_sha256'])
        self.assertNotIn(SLICE, graph['graph']['input_sha256'])
        self.assert_current()
        (self.root / alternate).write_text('{}')
        self.assert_stale([alternate])

    def test_invalid_active_record_refused_by_both_helpers(self):
        self.publish()
        self.assert_current()
        state = self.root / STATE
        for invalid in ('../../outside.json', '.warlock-contributor/../outside.json', None):
            with self.subTest(active_record=invalid):
                state.write_text(json.dumps({'activeContributorRecord': invalid}))
                with self.assertRaisesRegex(RuntimeError, 'Invalid active contributor record'):
                    ctx.load()
                with self.assertRaisesRegex(RuntimeError, 'Invalid active contributor record'):
                    gpu.graph()
        state.write_text(json.dumps({'activeContributorRecord': SLICE}))
        self.assert_current()

    def test_record_switch_during_extraction_refuses_publication(self):
        alternate = '.warlock-contributor/alternate.json'
        shutil.copyfile(self.root / SLICE, self.root / alternate)
        real_files = ctx.files
        calls = 0

        def switch_after_state_read():
            nonlocal calls
            calls += 1
            if calls == 1:
                (self.root / STATE).write_text(json.dumps({'activeContributorRecord': alternate}))
            return real_files()

        with patch.object(ctx, 'files', side_effect=switch_after_state_read):
            with self.assertRaisesRegex(RuntimeError, 'inputs changed during update'):
                ctx.update()
        self.assertFalse(self.graph.exists())
        self.assert_current_after_publish()

    def test_transient_source_removal_keeps_snapshotted_nodes(self):
        source = self.root / MODEL
        original = source.read_bytes()
        real_snapshot = ctx.read_inputs
        calls = 0

        def remove_then_restore():
            nonlocal calls
            calls += 1
            if calls == 1:
                snapshot = real_snapshot()
                source.unlink()
                return snapshot
            if calls == 2:
                source.write_bytes(original)
            return real_snapshot()

        try:
            with patch.object(ctx, 'read_inputs', side_effect=remove_then_restore):
                graph = self.publish()
        finally:
            if not source.exists():
                source.write_bytes(original)
        self.assertEqual(calls, 2)
        self.assertTrue(any(n.get('source_file') == MODEL and n.get('label') == 'ui_origin'
                            and n.get('kind') == 'module' for n in graph['nodes']))
        self.assert_current()

    def assert_current_after_publish(self):
        graph = self.publish()
        self.assertIn('.warlock-contributor/alternate.json', graph['graph']['input_sha256'])
        self.assertNotIn(SLICE, graph['graph']['input_sha256'])
        self.assert_current()

    def test_hq_delegates_budget_device_and_question_without_fallback(self):
        args = ['warlock-ctx', 'hq', '--device', 'cpu', '--budget', '413',
                'Which requirement denies remote navigation?']
        with patch.object(sys, 'argv', args), \
             patch.object(ctx.os, 'execv', side_effect=SystemExit(19)) as execute:
            with self.assertRaises(SystemExit) as raised:
                ctx.main()
        self.assertEqual(raised.exception.code, 19)
        wrapper = str(self.root / 'tools/warlock-gpu')
        execute.assert_called_once_with(wrapper, [wrapper, '--device', 'cpu',
                                                   '--budget', '413', 'hq', args[-1]])

    def test_keyword_budget_after_question_is_honored(self):
        self.publish()
        with patch.object(sys, 'argv', ['warlock-ctx', 'q', 'source terms', '--budget', '371']), \
             patch.object(ctx, '_query_graph_text', return_value='fixture') as query:
            ctx.main()
        self.assertEqual(query.call_args.kwargs['token_budget'], 371)


if __name__ == '__main__':
    unittest.main()

"""Fixture-level checks; run via an independently reviewed protected QA runner."""
import copy
import unittest
from toolchain_derivative import validate_profile


class DerivativeTests(unittest.TestCase):
    def setUp(self):
        self.ui = {'schema': 1, 'elfInputs': {'/a': {'sha256': 'a'}, '/b': {'sha256': 'b'}}}
        self.quint = {'schema': 1, 'path': '/q', 'version': '0.33.0', 'files': 1,
                      'treeSHA256': 'c', 'backend': 'typescript',
                      'node': {'path': '/node', 'sha256': 'd'}}
        self.packet = {'schema': 1, 'profile': 'host-20261102',
                       'parents': {'ui': 'U', 'quint': 'Q'},
                       'uiElfChanges': {'/a': {'before': 'a', 'after': 'e'}},
                       'quint': {'files': 1, 'treeSHA256': 'f'}}

    def test_exact_derived_inventory(self):
        ui, quint = validate_profile(self.packet, self.ui, self.quint, 'U', 'Q', {'/a'})
        self.assertEqual(ui['elfInputs']['/a']['sha256'], 'e')
        self.assertEqual(ui['elfInputs']['/b']['sha256'], 'b')
        self.assertEqual(quint['treeSHA256'], 'f')
        self.assertEqual(self.ui['elfInputs']['/a']['sha256'], 'a')

    def test_rejects_unreviewed_profile_or_parent_or_deltas(self):
        for edit in ('schema-bool', 'profile', 'parent', 'extra', 'before', 'missing', 'unknown'):
            p = copy.deepcopy(self.packet)
            if edit == 'schema-bool': p['schema'] = True
            if edit == 'profile': p['profile'] = 'other'
            if edit == 'parent': p['parents']['quint'] = 'wrong'
            if edit == 'extra': p['uiElfChanges']['/b'] = {'before': 'b', 'after': 'z'}
            if edit == 'before': p['uiElfChanges']['/a']['before'] = 'wrong'
            if edit == 'missing': del p['uiElfChanges']['/a']
            if edit == 'unknown': p['unexpected'] = True
            with self.subTest(edit=edit), self.assertRaises(RuntimeError):
                validate_profile(p, self.ui, self.quint, 'U', 'Q', {'/a'})

# These tests exercise the actual inventory verifier with private temporary data.
# They must be run by an explicitly reviewed protected runner, not on the live tree.
class QuintInventoryTests(unittest.TestCase):
    def test_file_symlink_and_count_mutation_fail(self):
        import hashlib
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        import check_elm_cpu
        import toolchain_derivative
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'file').write_text('baseline')
            (root / 'link').symlink_to('file')
            sha = hashlib.sha256((root / 'file').read_bytes()).hexdigest()
            rows = {'file': {'sha256': sha}, 'link': {'symlink': 'file', 'sha256': sha}}
            tree = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            pin = {'path': str(root), 'files': 2, 'treeSHA256': tree, 'backend': 'typescript'}
            with patch.object(toolchain_derivative, 'selected', return_value=({}, pin, {})):
                check_elm_cpu.quint_toolchain()
                (root / 'file').write_text('changed')
                with self.assertRaises(RuntimeError): check_elm_cpu.quint_toolchain()
                (root / 'file').write_text('baseline')
                (root / 'link').unlink()
                (root / 'link').symlink_to('missing')
                with self.assertRaises(RuntimeError): check_elm_cpu.quint_toolchain()
                (root / 'link').unlink()
                with self.assertRaises(RuntimeError): check_elm_cpu.quint_toolchain()


class UiInventoryTests(unittest.TestCase):
    def test_real_ui_inventory_rejects_source_and_link_mutations(self):
        import hashlib
        import os
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        import toolchain_derivative
        import ui_host_toolchain
        for mutation in ('changed', 'extra', 'missing', 'mode', 'symlink', 'elf', 'elf-symlink'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp)
                sdk = base / 'sdk'
                sdk.mkdir()
                member = sdk / 'member'
                member.write_bytes(b'held')
                member.chmod(0o644)
                alias = sdk / 'alias'
                alias.symlink_to('member')
                elf = base / 'library.so'
                elf.write_bytes(b'elf-input')
                def sha(path):
                    return hashlib.sha256(path.read_bytes()).hexdigest()
                packet = {'schema': 1, 'sdkDirectory': '/home/charl/.cache/warlock-ui-host/sdk',
                          'libraryDirectory': str(sdk),
                          'files': {'member': {'sha256': sha(member), 'mode': '0o644', 'bytes': 4},
                                    'alias': {'symlink': 'member', 'resolvedSHA256': sha(member)}},
                          'elfInputs': {str(elf): {'sha256': sha(elf)}}}
                def selected_path(value):
                    return sdk if str(value) == packet['sdkDirectory'] else Path(value)
                with patch.object(toolchain_derivative, 'selected', return_value=(packet, {}, {})), \
                     patch.object(ui_host_toolchain, 'Path', side_effect=selected_path):
                    ui_host_toolchain.verify()
                    if mutation == 'changed': member.write_bytes(b'other')
                    elif mutation == 'extra': (sdk / 'extra').write_bytes(b'extra')
                    elif mutation == 'missing': member.unlink()
                    elif mutation == 'mode': member.chmod(0o600)
                    elif mutation == 'symlink': alias.unlink(); alias.symlink_to('../library.so')
                    elif mutation == 'elf': elf.write_bytes(b'different')
                    elif mutation == 'elf-symlink':
                        other = base / 'other.so'
                        other.write_bytes(elf.read_bytes())
                        elf.unlink()
                        elf.symlink_to(other)
                    with self.assertRaises(RuntimeError):
                        ui_host_toolchain.verify()

class SelectionFilesystemTests(unittest.TestCase):
    def test_selected_binds_bytes_and_rejects_symlink_and_parent_change(self):
        import hashlib
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        import toolchain_derivative as selection
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            original = (selection.PROFILE, selection.UI_PARENT, selection.QUINT_PARENT)
            copies = [tmp / p.name for p in original]
            for source, dest in zip(original, copies): dest.write_bytes(source.read_bytes())
            with patch.object(selection, 'PROFILE', copies[0]), patch.object(selection, 'UI_PARENT', copies[1]), patch.object(selection, 'QUINT_PARENT', copies[2]):
                _, pin, identity = selection.selected()
                self.assertEqual(identity['derivativeSHA256'], hashlib.sha256(copies[0].read_bytes()).hexdigest())
                packet = json.loads(copies[0].read_bytes())
                name = next(iter(packet['uiElfChanges']))
                for field in ('elf', 'tree'):
                    altered = copy.deepcopy(packet)
                    if field == 'elf': altered['uiElfChanges'][name]['after'] = 'e' * 64
                    else: altered['quint']['treeSHA256'] = 'f' * 64
                    copies[0].write_text(json.dumps(altered))
                    _, changed, new_identity = selection.selected()
                    self.assertNotEqual(new_identity['derivativeSHA256'], identity['derivativeSHA256'])
                    if field == 'tree': self.assertNotEqual(changed['treeSHA256'], pin['treeSHA256'])
                copies[0].write_bytes(original[0].read_bytes())
                for index in range(3):
                    data = copies[index].read_bytes()
                    copies[index].unlink()
                    copies[index].symlink_to(original[index])
                    with self.subTest(symlink=index), self.assertRaises(RuntimeError): selection.selected()
                    copies[index].unlink()
                    copies[index].write_bytes(data)
                copies[1].write_bytes(copies[1].read_bytes() + b' ')
                with self.assertRaises(RuntimeError): selection.selected()


class ReviewedLockTests(unittest.TestCase):
    def test_profile_and_selector_mutations_before_launch_or_after_child_rejected(self):
        import hashlib
        import json
        import os
        import sys
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        import qa_cpu
        for changed in ('tools/host-toolchain-derivative.json', 'tools/toolchain_derivative.py'):
            for when in ('lock', 'child'):
                with self.subTest(changed=changed, when=when), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp); (root / 'tools').mkdir(); runtime = root / 'runtime'; runtime.mkdir()
                    names = {'tools/check_registry_cpu.py', 'tools/host-toolchain-derivative.json', 'tools/toolchain_derivative.py'}
                    for name in names: (root / name).write_text('original')
                    profile = root / 'tools/host-toolchain-derivative.json'
                    profile.write_text(json.dumps({'uiElfChanges': {'/a': {'after': 'a' * 64}}, 'quint': {'files': 1, 'treeSHA256': 'b' * 64}}))
                    inputs = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}
                    packet = {'schema': 1, 'runner': str(root / 'tools/check_registry_cpu.py'), 'arguments': [], 'inputs': inputs}
                    review = root / 'review.json'; review.write_text(json.dumps(packet))
                    sha = hashlib.sha256(review.read_bytes()).hexdigest()
                    def mutate():
                        if changed.endswith('.json'):
                            value = json.loads(profile.read_text())
                            value['uiElfChanges']['/a']['after'] = 'e' * 64
                            value['quint']['treeSHA256'] = 'f' * 64
                            profile.write_text(json.dumps(value))
                        else:
                            (root / changed).write_text('unreviewed')
                    class Child:
                        pid = 123
                        returncode = 0
                        def wait(self, timeout):
                            if when == 'child': mutate()
                            return 0
                    called = []
                    def popen(*args, **kwargs): called.append(True); return Child()
                    def flock(fd, flags):
                        if when == 'lock': mutate()
                    with patch.object(qa_cpu, 'REPO', root), patch.object(qa_cpu, 'registry_inputs', return_value=names), \
                         patch.object(qa_cpu, 'require_qa_scope'), patch.object(qa_cpu, 'runtime_base', return_value=runtime), \
                         patch.object(qa_cpu.fcntl, 'flock', side_effect=flock), patch.object(qa_cpu.subprocess, 'Popen', side_effect=popen), \
                         patch.object(sys, 'argv', ['qa_cpu.py', '--inside-scope', '--review', str(review), '--sha256', sha]):
                        with self.assertRaisesRegex(RuntimeError, '(Reviewed input missing or changed|Post-run review check failed)') as raised: qa_cpu.main()
                    self.assertIn(changed, str(raised.exception) + str(raised.exception.__cause__))
                    self.assertEqual(bool(called), when == 'child')


class ReceiptNodeTests(unittest.TestCase):
    def test_receipt_branch_wrong_node_invokes_no_model(self):
        import hashlib
        import tempfile
        import textwrap
        from pathlib import Path
        from types import SimpleNamespace
        import check_elm_cpu
        source = Path(check_elm_cpu.__file__).read_text()
        branch = source[source.index('        if args.receipts:\n'):source.index('        if args.browser:\n', source.index('        if args.receipts:\n'))]
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); root = base / 'root'; work = base / 'work'
            (root / 'qa').mkdir(parents=True); (work / 'qa').mkdir(parents=True)
            (base / 'tools').mkdir(); (base / 'tools/quint-toolchain.json').write_text('{}')
            for name in ('receipt-lifecycle.qnt', 'receipt-lifecycle_test.qnt'): (root / 'qa' / name).write_text('fixture')
            good = base / 'node'; other = base / 'other'
            good.write_bytes(b'node'); other.write_bytes(b'node')
            good_hash = hashlib.sha256(good.read_bytes()).hexdigest()
            for node, sha in ((other, good_hash), (good, '0' * 64)):
                pin = {'node': {'path': str(good), 'sha256': sha}}
                calls = []
                def run(*args):
                    calls.append(args)
                    raise RuntimeError('unexpected model invocation')
                scope = dict(check_elm_cpu.__dict__)
                scope.update(args=SimpleNamespace(receipts=True), root=root, work=work, REPO=base,
                             output=base, node=node, report={}, sources={},
                             quint_toolchain=lambda: (pin, base / 'cli'), run=run)
                with self.subTest(node=node, sha=sha), self.assertRaisesRegex(RuntimeError, 'Pinned model interpreter differs'):
                    exec(compile(textwrap.dedent(branch), '<receipt-branch>', 'exec'), scope)
                self.assertEqual(calls, [])

if __name__ == '__main__':
    unittest.main()

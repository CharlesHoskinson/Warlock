"""Capture-oracle boundary tests; actual focus/selection equality still needs native proof."""
import ast
import copy
from pathlib import Path
import tempfile
import unittest


def methods():
    source = ast.parse(Path(__file__).with_name('run_native.py').read_text())
    nodes = [n for n in source.body if isinstance(n, ast.FunctionDef) and n.name in ['captured_rename_source', 'prompt_captures_source']]
    namespace = {'Path': Path}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual-rename-capture>', 'exec'), namespace)
    return namespace


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='files-rename-capture-')
        self.home = Path(self.temp.name)
        self.fixture = self.home / 'fixture'
        self.fixture.mkdir()
        self.source = self.fixture / 'image.svg'
        self.source.write_bytes(b'private diagnostic fixture')
        self.peer = {'valid': True, 'role': 34, 'logicalIdentity': 'file:' + str(self.source)}
        self.public = {'sel': ['image.svg']}
        self.ui = {'sel': {str(self.source): True}, 'nsel': 1, 'cwd': str(self.fixture), 'cur': 1}
        self.methods = methods()

    def tearDown(self):
        self.temp.cleanup()

    def test_coherent_image_source_captured_without_alpha_assumption(self):
        actual = self.methods['captured_rename_source'](self.peer, self.public, self.ui, self.home)
        self.assertEqual(actual, self.source)

    def test_public_or_full_selection_mismatch_refused(self):
        for public, ui in [({'sel': ['alpha.txt']}, self.ui), (self.public, dict(self.ui, sel={str(self.fixture / 'alpha.txt'): True})),
                           (self.public, dict(self.ui, nsel=2)), (self.public, dict(self.ui, cur=-1)),
                           (self.public, dict(self.ui, cwd=str(self.home)))]:
            with self.assertRaises(AssertionError):
                self.methods['captured_rename_source'](self.peer, public, ui, self.home)

    def test_nonfile_peer_scope_or_missing_source_refused(self):
        for peer in [dict(self.peer, role=43), dict(self.peer, valid=False),
                     dict(self.peer, logicalIdentity='recent:' + str(self.source)),
                     dict(self.peer, logicalIdentity='file:' + str(self.fixture)),
                     dict(self.peer, logicalIdentity='file:/outside/fixture.txt')]:
            with self.assertRaises(AssertionError):
                self.methods['captured_rename_source'](peer, self.public, self.ui, self.home)

    def test_f2_captured_payload_and_original_input_must_match_source(self):
        good = {'visible': True, 'mode': 'rename', 'payload': {'path': str(self.source)}, 'text': self.source.name}
        check = self.methods['prompt_captures_source']
        self.assertTrue(check(good, self.source))
        for key, value in [('visible', False), ('mode', 'mkdir'), ('payload', {'path': str(self.fixture / 'alpha.txt')}), ('text', 'alpha.txt')]:
            changed = copy.deepcopy(good)
            changed[key] = value
            self.assertFalse(check(changed, self.source), key)


if __name__ == '__main__':
    unittest.main()

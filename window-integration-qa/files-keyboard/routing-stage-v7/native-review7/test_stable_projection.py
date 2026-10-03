"""Verify the executed client projection and its title boundary, without desktop access."""
import ast
import copy
from pathlib import Path
import types
import unittest
import preservation


class ProjectionTests(unittest.TestCase):
    def test_exact_stable_fields_and_observed_title(self):
        source = ast.parse(Path(__file__).with_name('run_native.py').read_text())
        function = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'canonical_clients')
        namespace = {'preservation': preservation}
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<actual-client-projection>', 'exec'), namespace)
        project = namespace['canonical_clients']
        fields = preservation.CLIENT_FIELDS + ('mapped', 'hidden', 'visible', 'acceptsInput', 'class',
            'initialClass', 'initialTitle', 'xwayland', 'pinFullscreened', 'fullscreenHandler',
            'allowedOverFullscreen', 'swallowing', 'inhibitingIdle', 'xdgTag', 'xdgDescription',
            'contentType', 'tearingHint')
        row = {name: 'original-' + name for name in fields}
        row['title'] = 'application-owned title before'
        self.assertEqual(set(project([row])[0]), set(fields))
        changed = copy.deepcopy(row)
        changed['title'] = 'application-owned spinner title after'
        self.assertEqual(project([row]), project([changed]))
        for name in fields:
            changed = copy.deepcopy(row)
            changed[name] = 'changed-' + name
            self.assertNotEqual(project([row]), project([changed]), name)


if __name__ == '__main__':
    unittest.main()

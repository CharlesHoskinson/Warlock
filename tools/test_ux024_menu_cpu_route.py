#!/usr/bin/env python3
"""Root-only pure admission/result controls; no compiler or DOM fixture execution."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

QA_PATH, ELM_PATH, REPOSITORY = map(Path, sys.argv[1:4])
sys.argv = [sys.argv[0], *sys.argv[4:]]
sys.path.insert(0, str(REPOSITORY / 'window-integration-qa'))
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = REPOSITORY
    return module
qa = load('menu_test_qa_cpu', QA_PATH)
elm = load('menu_test_check_elm', ELM_PATH)

class FixedMenuRoute(unittest.TestCase):
    def valid(self):
        return {'passed': True, 'cases': [{'name': n, 'passed': True} for n in elm.MENU_TAB_CASES],
                'checks': [{'name': 'actual assertion', 'passed': True}], 'failures': [],
                'nativeAcceptance': False, 'originalAccepted': False}
    def test_exact_mode_only(self):
        runner = REPOSITORY / 'tools/check_elm_cpu.py'
        self.assertTrue(qa.menu_tab_dom_mode(runner, ['--menu-tab-dom', '--arm64']))
        for args in [[], ['--menu-tab-dom'], ['--arm64', '--menu-tab-dom'],
                     ['--menu-tab-dom', '--arm64', '--script', '/tmp/other.cjs'], ['--subscriptions']]:
            self.assertFalse(qa.menu_tab_dom_mode(runner, args))
    def test_foreign_runner_refuses(self):
        self.assertFalse(qa.menu_tab_dom_mode(REPOSITORY / 'tools/other.py', ['--menu-tab-dom', '--arm64']))
    def test_complete_source_membership(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            src = root / 'implementation/warlock/src'
            (src / 'Nested').mkdir(parents=True)
            (src / 'HttpPopup.elm').write_text('')
            (src / 'Nested/Dependency.elm').write_text('')
            result = qa.menu_tab_dom_inputs(root)
            self.assertIn('implementation/warlock/src/HttpPopup.elm', result)
            self.assertIn('implementation/warlock/src/Nested/Dependency.elm', result)
            self.assertIn('implementation/warlock/qa/ux024-menu-dom.cjs', result)
            self.assertIn('tools/arm64_toolchain.py', result)
            self.assertIn('window-integration-qa/qa_launch.py', result)
            self.assertNotIn('implementation/warlock/qa/ui-http.cjs', result)
    def test_exact_success_result(self):
        self.assertEqual(len(elm.MENU_TAB_CASES), 18)
        elm.validate_menu_tab_result(self.valid())
    def test_missing_empty_extra_duplicate_case_refuse(self):
        for mutation in ['missing', 'empty', 'extra', 'duplicate']:
            value = self.valid()
            if mutation == 'missing': value['cases'].pop()
            if mutation == 'empty': value['cases'] = []
            if mutation == 'extra': value['cases'].append({'name': 'extra', 'passed': True})
            if mutation == 'duplicate': value['cases'][-1] = copy.deepcopy(value['cases'][0])
            with self.assertRaises(RuntimeError): elm.validate_menu_tab_result(value)
    def test_failed_skipped_case_refuses(self):
        for change in [{'passed': False}, {'passed': True, 'skipped': True}]:
            value = self.valid(); value['cases'][0].update(change)
            with self.assertRaises(RuntimeError): elm.validate_menu_tab_result(value)
    def test_false_summary_or_failed_assertion_refuses(self):
        for name in ['summary', 'check', 'failures', 'empty-checks']:
            value = self.valid()
            if name == 'summary': value['passed'] = False
            if name == 'check': value['checks'][0]['passed'] = False
            if name == 'failures': value['failures'] = [{'name': 'failure'}]
            if name == 'empty-checks': value['checks'] = []
            with self.assertRaises(RuntimeError): elm.validate_menu_tab_result(value)
    def test_profile_requires_exact_parent_values(self):
        parent = json.loads((REPOSITORY / 'tools/arm64-toolchain.json').read_text())
        profile = json.loads((ELM_PATH.parent / 'menu-tab-elm-toolchain.json').read_text())
        elm.validate_menu_tab_profile(profile, parent, elm.MENU_TAB_PARENT_SHA)
        for field in ['elm', 'node', 'cacheInventory', 'elmHome', 'originalManifest']:
            changed = copy.deepcopy(profile)
            if field == 'elmHome': changed[field] += '/other'
            elif field == 'cacheInventory': changed[field] = {}
            elif field == 'originalManifest': changed[field]['sha256'] = '0' * 64
            else: changed[field]['sha256'] = '0' * 64
            with self.assertRaises(RuntimeError):
                elm.validate_menu_tab_profile(changed, parent, elm.MENU_TAB_PARENT_SHA)
    def test_profile_scope_and_extra_fields_refuse(self):
        parent = json.loads((REPOSITORY / 'tools/arm64-toolchain.json').read_text())
        profile = json.loads((ELM_PATH.parent / 'menu-tab-elm-toolchain.json').read_text())
        for change in [{'scope': 'native'}, {'architecture': 'x86_64'}, {'arbitraryCommand': 'node'}]:
            changed = copy.deepcopy(profile); changed.update(change)
            with self.assertRaises(RuntimeError):
                elm.validate_menu_tab_profile(changed, parent, elm.MENU_TAB_PARENT_SHA)
    def test_native_or_original_credit_refuses(self):
        for field in ['nativeAcceptance', 'originalAccepted']:
            value = self.valid(); value[field] = True
            with self.assertRaises(RuntimeError): elm.validate_menu_tab_result(value)

if __name__ == '__main__': unittest.main()

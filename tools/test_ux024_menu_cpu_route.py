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


class FixedMenuEscapeRoute(unittest.TestCase):
    def valid(self):
        return {'passed': True, 'classification': 'component-pass', 'caseCount': 16,
                'nativeAcceptance': False, 'originalAccepted': False,
                'imageSha256': 'a'*64, 'fixtureSha256': 'b'*64,
                'observed': {'preconditions': {n: True for n in elm.MENU_ESCAPE_PRECONDITIONS},
                             'checks': {n: True for n in elm.MENU_ESCAPE_CASES}},
                'checks': [{'name': n, 'passed': True} for n in elm.MENU_ESCAPE_CASES], 'failures': []}
    def check(self,value):
        elm.validate_menu_escape_result(value,'a'*64,'b'*64)
    def test_escape_exact_success(self):
        self.check(self.valid())
    def test_escape_missing_extra_duplicate_case_refuses(self):
        for mode in ['missing','extra','duplicate']:
            v=self.valid()
            if mode=='missing':v['checks'].pop()
            if mode=='extra':v['checks'].append({'name':'extra','passed':True})
            if mode=='duplicate':v['checks'][-1]=copy.deepcopy(v['checks'][0])
            with self.assertRaises(RuntimeError):self.check(v)
    def test_escape_setup_inventory_and_nonboolean_refuse(self):
        for mode in ['missing','false','nonboolean','extra']:
            v=self.valid();p=v['observed']['preconditions'];n=next(iter(p))
            if mode=='missing':p.pop(n)
            if mode=='false':p[n]=False
            if mode=='nonboolean':p[n]=1
            if mode=='extra':p['extra']=True
            with self.assertRaises(RuntimeError):self.check(v)
    def test_escape_failed_red_or_skipped_result_refuses(self):
        for mode in ['row','red','summary','failures','skipped']:
            v=self.valid()
            if mode=='row':v['checks'][0]['passed']=False
            if mode=='red':v['classification']='semantic-red'
            if mode=='summary':v['passed']=False
            if mode=='failures':v['failures']=[{'name':'actual failure'}]
            if mode=='skipped':v['checks'][0]['skipped']=True
            with self.assertRaises(RuntimeError):self.check(v)
    def test_escape_wrong_artifact_or_acceptance_refuses(self):
        for field,value in [('imageSha256','0'*64),('fixtureSha256','0'*64),('nativeAcceptance',True),('originalAccepted',True)]:
            v=self.valid();v[field]=value
            with self.assertRaises(RuntimeError):self.check(v)
    def test_escape_fixed_dependency_membership(self):
        with tempfile.TemporaryDirectory() as temp:
            inputs=qa.menu_tab_dom_inputs(Path(temp))
            self.assertTrue(set(elm.MENU_ESCAPE_QA_INPUTS)<=inputs)
            self.assertEqual(len(elm.MENU_ESCAPE_QA_INPUTS),3)
            self.assertIn('implementation/warlock/qa/OutputRetirementReplay.elm',inputs)
            self.assertNotIn('implementation/warlock/qa/arbitrary.cjs',inputs)


class FixedBarContextRoute(unittest.TestCase):
    def valid(self):
        return {'schema':1,'passed':True,'classification':'component-pass','inventoryMatches':True,
                'nativeAcceptance':False,'originalAccepted':False,'failures':[],
                'artifactHashes':{'image':'a'*64,'harness':'b'*64},
                'seededKeyboard':{'algorithm':'xorshift32','seeds':list(range(32)),'sampleCount':32,
                    'samples':[{'seed':i,'allowed':i%8==0,'defaultPrevented':i%8==0,'posts':[{}] if i%8==0 else []} for i in range(32)]},
                'cases':[{'name':n,'passed':True} for n in elm.MENU_BAR_CONTEXT_CASES],
                'checks':[{'name':'actual transport assertion','passed':True}]}
    def check(self,value):elm.validate_menu_bar_context_result(value,'a'*64,'b'*64)
    def test_bar_context_exact_success(self):self.check(self.valid())
    def test_bar_context_missing_extra_duplicate_case_refuses(self):
        for mode in ['missing','extra','duplicate']:
            value=self.valid()
            if mode=='missing':value['cases'].pop()
            if mode=='extra':value['cases'].append({'name':'extra','passed':True})
            if mode=='duplicate':value['cases'][-1]=copy.deepcopy(value['cases'][0])
            with self.assertRaises(RuntimeError):self.check(value)
    def test_bar_context_failed_setup_red_inventory_refuses(self):
        for field,value in [('setupFailures',1),('classification','semantic-red'),('classification','fixture-setup-failed'),('inventoryMatches',False),('passed',False)]:
            report=self.valid();report[field]=value
            with self.assertRaises(RuntimeError):self.check(report)
        for mode in ['missing','duplicate','short','nonbool','positive']:
            report=self.valid();seeded=report['seededKeyboard']
            if mode=='missing':report.pop('seededKeyboard')
            if mode=='duplicate':seeded['seeds'][-1]=0
            if mode=='short':seeded['samples'].pop()
            if mode=='nonbool':seeded['samples'][1]['allowed']=0
            if mode=='positive':seeded['samples'][0].update(allowed=False,defaultPrevented=False,posts=[])
            with self.assertRaises(RuntimeError):self.check(report)
    def test_bar_context_wrong_image_or_harness_refuses(self):
        for field in ['image','harness']:
            report=self.valid();report['artifactHashes'][field]='0'*64
            with self.assertRaises(RuntimeError):self.check(report)
    def test_bar_context_failed_skipped_or_acceptance_refuses(self):
        for mode in ['case','check','skipped','empty','failures','native','original']:
            report=self.valid()
            if mode=='case':report['cases'][0]['passed']=False
            if mode=='check':report['checks'][0]['passed']=False
            if mode=='skipped':report['checks'][0]['skipped']=True
            if mode=='empty':report['checks']=[]
            if mode=='failures':report['failures']=[{'name':'actual failure'}]
            if mode=='native':report['nativeAcceptance']=True
            if mode=='original':report['originalAccepted']=True
            with self.assertRaises(RuntimeError):self.check(report)
    def test_bar_context_one_fixed_input_added(self):
        with tempfile.TemporaryDirectory() as temp:
            inputs=qa.menu_tab_dom_inputs(Path(temp))
            self.assertIn(elm.MENU_BAR_CONTEXT_FIXTURE,inputs)
            self.assertEqual(elm.MENU_BAR_CONTEXT_FIXTURE,'implementation/warlock/qa/ux024-bar-context-dom.cjs')
            self.assertIn('implementation/warlock/qa/ux024-menu-dom.cjs',inputs)
            self.assertTrue(set(elm.MENU_ESCAPE_QA_INPUTS)<=inputs)


class FixedMenuInitialFocusRoute(unittest.TestCase):
    def valid(self):
        return {'schema':1,'passed':True,'classification':'component-pass','caseCount':17,
                'nativeAcceptance':False,'originalAccepted':False,'failures':[],'seedFailures':[],'seedSampleCount':32,
                'imageSha256':'a'*64,'fixtureSha256':'b'*64,
                'observed':{'preconditions':{n:True for n in elm.MENU_INITIAL_FOCUS_PRECONDITIONS},'checks':{n:True for n in elm.MENU_INITIAL_FOCUS_CASES}},
                'checks':[{'name':n,'passed':True} for n in elm.MENU_INITIAL_FOCUS_CASES],
                'seeded':{'algorithm':'literal-seed-modulo8-public-event-sequence','seeds':list(range(32)),
                          'samples':[{'seed':i,'passed':True} for i in range(32)]}}
    def check(self,value):elm.validate_menu_initial_focus_result(value,'a'*64,'b'*64)
    def test_initial_focus_exact_success(self):self.check(self.valid())
    def test_initial_focus_missing_extra_duplicate_case_refuses(self):
        for mode in ['missing','extra','duplicate']:
            v=self.valid()
            if mode=='missing':v['checks'].pop()
            if mode=='extra':v['checks'].append({'name':'extra','passed':True})
            if mode=='duplicate':v['checks'][-1]=copy.deepcopy(v['checks'][0])
            with self.assertRaises(RuntimeError):self.check(v)
    def test_initial_focus_precondition_inventory_refuses(self):
        for mode in ['missing','false','nonbool','extra']:
            v=self.valid();p=v['observed']['preconditions'];n=next(iter(p))
            if mode=='missing':p.pop(n)
            if mode=='false':p[n]=False
            if mode=='nonbool':p[n]=1
            if mode=='extra':p['extra']=True
            with self.assertRaises(RuntimeError):self.check(v)
    def test_initial_focus_failed_red_seed_loss_refuses(self):
        for mode in ['failed','red','seedlist','samples','seedfailure','summary']:
            v=self.valid()
            if mode=='failed':v['checks'][0]['passed']=False
            if mode=='red':v['classification']='semantic-red'
            if mode=='seedlist':v['seeded']['seeds'][-1]=0
            if mode=='samples':v['seeded']['samples'].pop()
            if mode=='seedfailure':v['seedFailures']=[{'seed':0}]
            if mode=='summary':v['passed']=False
            with self.assertRaises(RuntimeError):self.check(v)
    def test_initial_focus_wrong_artifact_acceptance_refuses(self):
        for field,value in [('imageSha256','0'*64),('fixtureSha256','0'*64),('nativeAcceptance',True),('originalAccepted',True)]:
            v=self.valid();v[field]=value
            with self.assertRaises(RuntimeError):self.check(v)
    def test_initial_focus_two_fixed_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            inputs=qa.menu_tab_dom_inputs(Path(temp))
            self.assertEqual(len(elm.MENU_INITIAL_FOCUS_QA_INPUTS),2)
            self.assertTrue(set(elm.MENU_INITIAL_FOCUS_QA_INPUTS)<=inputs)
            self.assertIn('implementation/warlock/qa/OutputRetirementReplay.elm',inputs)

if __name__ == '__main__': unittest.main()

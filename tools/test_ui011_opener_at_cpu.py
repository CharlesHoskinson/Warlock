#!/usr/bin/env python3
"""Root-only fixed admission/result controls. No compiler, opener, or bus execution."""
import ast, importlib.util, sys, unittest
from pathlib import Path
QA,RUNNER,REPO=map(Path,sys.argv[1:4]);sys.argv=[sys.argv[0],*sys.argv[4:]]
sys.path.insert(0,str(REPO/'window-integration-qa'))
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
qa=load('opener_qa',QA);qa.REPO=REPO
runner=load('opener_runner',RUNNER)
def output(red=False):
 rows=[f"owned-at:{n}={'PASS' if not red or n in {runner.AT_NAMES[0],'shared-runtime-refused'} else 'FAIL'}" for n in runner.AT_NAMES]
 rows += [f"owned-at:literal-seed-{i}={'PASS' if not red or i%4==1 else 'FAIL'}" for i in range(32)]
 return '\n'.join(rows)+'\n'
def failure_resets_passed(handler):
 if not isinstance(handler,ast.ExceptHandler) or not handler.body:return False
 first=handler.body[0]
 if isinstance(first,ast.Assign):
  return len(first.targets)==1 and ast.unparse(first.targets[0])=="report['passed']" and isinstance(first.value,ast.Constant) and first.value.value is False
 if isinstance(first,ast.Expr) and isinstance(first.value,ast.Call):
  call=first.value
  return ast.unparse(call.func)=='report.update' and not call.args and any(k.arg=='passed' and isinstance(k.value,ast.Constant) and k.value.value is False for k in call.keywords)
 return False
class FixedOpenerAT(unittest.TestCase):
 def test_only_fixed_four_targets(self):
  self.assertEqual(runner.TARGETS,(('ui011-opener-fixture','warlock-runtime:exe:ui011-opener-fixture'),('ui011-opener-admission-controls','warlock-runtime:test:ui011-opener-admission-controls'),('ui-display-controls','warlock-runtime:test:ui-display-controls'),('ui-engine-controls','warlock-runtime:test:ui-engine-controls')))
 def test_exact_admission(self):self.assertTrue(qa.opener_at_cpu_mode(REPO/qa.OPENER_AT_CPU_RUNNER,['opener-at','--manifest-sha256','a'*64],'a'*64))
 def test_other_arguments_refuse(self):
  for args in [[],['protocol','--manifest-sha256','a'*64],['opener-at','--manifest-sha256','b'*64],['opener-at','--manifest-sha256','a'*64,'--inside-private','/tmp']]:
   self.assertFalse(qa.opener_at_cpu_mode(REPO/qa.OPENER_AT_CPU_RUNNER,args,'a'*64))
 def test_other_runner_refuses(self):self.assertFalse(qa.opener_at_cpu_mode(REPO/'tools/other.py',['opener-at','--manifest-sha256','a'*64],'a'*64))
 def test_legacy_modes_retained(self):
  self.assertTrue(qa.window_watch_protocol_mode(REPO/qa.WINDOW_WATCH_PROTOCOL_RUNNER,['protocol','--manifest-sha256','a'*64],'a'*64));self.assertTrue(qa.menu_tab_dom_mode(REPO/'tools/check_elm_cpu.py',['--menu-tab-dom','--arm64']))
 def test_full_green(self):self.assertTrue(runner.at_result(0,output())['passed'])
 def test_complete_semantic_red_remains_failure(self):
  r=runner.at_result(1,output(True));self.assertFalse(r['passed']);self.assertEqual(r['classification'],'at-transport-semantic-red');self.assertEqual(len(r['checks']),18);self.assertEqual(len(r['seeded']),32)
 def test_missing_fixed_result_refuses(self):
  with self.assertRaises(ValueError):runner.at_result(0,output().replace('owned-at:'+runner.AT_NAMES[0]+'=PASS\n',''))
 def test_missing_seed_refuses(self):
  with self.assertRaises(ValueError):runner.at_result(0,output().replace('owned-at:literal-seed-31=PASS\n',''))
 def test_duplicate_result_refuses(self):
  with self.assertRaises(ValueError):runner.at_result(0,output()+'owned-at:'+runner.AT_NAMES[0]+'=PASS\n')
 def test_false_exit_and_unexpected_failure_refuse(self):
  for code,text in [(1,output()),(0,output(True)),(1,output().replace('owned-at:'+runner.AT_NAMES[0]+'=PASS','owned-at:'+runner.AT_NAMES[0]+'=FAIL'))]:
   with self.assertRaises(ValueError):runner.at_result(code,text)
 def test_admission_exact_completion(self):
  self.assertTrue(runner.admission_result(0,runner.ADMISSION_SENTINEL+'\n')['passed'])
  for code,text in [(1,runner.ADMISSION_SENTINEL),(0,''),(0,runner.ADMISSION_SENTINEL+'\nextra')]:
   with self.assertRaises(ValueError):runner.admission_result(code,text)
 def test_opener_never_executed(self):
  t=ast.parse(RUNNER.read_text());calls=[n for n in ast.walk(t)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='run'];literal=[n.args[0].value for n in calls if n.args and isinstance(n.args[0],ast.Constant)];self.assertEqual(literal,['opener-admission-controls','at-transport-controls','ui-engine-controls']);self.assertIn('openerExecuted=False',RUNNER.read_text())
 def test_current_guards_and_original_budgets(self):
  t=RUNNER.read_text()
  for value in ["'opener-at':300",'min(120, deadline','child.wait(timeout=2)','build.verify_inputs(data)','build.require_group_absent(child)',"'--tmpfs', '/run', '--dir', '/run/user'"]:self.assertIn(value,t)
  handlers=[n for n in ast.walk(ast.parse(t)) if isinstance(n,ast.ExceptHandler) and isinstance(n.type,ast.Name) and n.type.id=='Exception']
  self.assertEqual(len(handlers),1)
  self.assertTrue(failure_resets_passed(handlers[0]))
  for body in ["report['passed'] = False", "report.update(passed=False, error=str(error))"]:
   sample=ast.parse('try:\n pass\nexcept Exception as error:\n '+body).body[0].handlers[0]
   self.assertTrue(failure_resets_passed(sample))
   mutant=ast.parse('try:\n pass\nexcept Exception as error:\n '+body.replace('False','True')).body[0].handlers[0]
   self.assertFalse(failure_resets_passed(mutant))
  for body in ["report['error'] = str(error)","report.update(error=str(error))"]:
   self.assertFalse(failure_resets_passed(ast.parse('try:\n pass\nexcept Exception as error:\n '+body).body[0].handlers[0]))
 def test_frozen_five_fixtures_and_private_strict_json(self):
  self.assertEqual(len(qa.OPENER_AT_FIXTURES),5);self.assertIn('Exact five frozen staged fixture paths required',QA.read_text());self.assertIn('runtime/fixture-ui011-opener/Warlock/Protocol/StrictJson.hs',RUNNER.read_text());self.assertIn('bytestring, containers, text,',RUNNER.read_text())
 def test_pure_admission_cannot_resolve_native_main(self):
  prefix='executable ui011-opener-fixture\n  main-is: Main.hs\n'
  good=prefix+'\ntest-suite ui011-opener-admission-controls\n  hs-source-dirs: test-ui011-opener\n  main-is: Main.hs\n'
  runner.require_admission_source_root(good)
  for bad in [good.replace('hs-source-dirs: test-ui011-opener','hs-source-dirs: test-ui011-opener, fixture-ui011-opener'),good.replace('hs-source-dirs: test-ui011-opener','hs-source-dirs: fixture-ui011-opener'),good.replace('main-is: Main.hs','main-is: Main.hsc')]:
   with self.assertRaises(ValueError):runner.require_admission_source_root(bad)
  text=RUNNER.read_text()
  self.assertIn("('OpenerAdmission.hs', 'runtime/test-ui011-opener/OpenerAdmission.hs')",text)
  self.assertIn("work / 'runtime/test-ui011-opener/Warlock/Protocol/StrictJson.hs'",text)
  self.assertIn('require_admission_source_root(stanza)',text)
if __name__=='__main__':unittest.main()

"""Unprojected actual new JS CPU fixture and original-source preservation."""
import ast,hashlib,json,subprocess,unittest
from pathlib import Path
from keyboard_preservation_projection import project
B=Path(__file__).resolve().parent;OLD=B.with_name('browser-files-flow-v17')
class Diagnostic(unittest.TestCase):
 def test_actual_new_javascript_21_cpu_cases(self):
  p=subprocess.run([str(B/'keyboard-diagnostic-cpu'),str(B/'KeyboardDiagnostic.js'),str(B/'keyboard_diagnostic_fixture.js')],capture_output=True,text=True,timeout=8)
  self.assertEqual(p.returncode,0,p.stderr);r=json.loads(p.stdout);self.assertEqual(r['cpuCases'],21);self.assertFalse(r['realDomEventProof']);self.assertFalse(r['nativeGuiExecuted'])
 def test_exact_original_fixture_callback_and_query_after_narrow_removal(self):
  for name in ('compose.html','cdp_readonly.py'):self.assertEqual(project(B/name,(B/name).read_text()),(OLD/name).read_text(),name)
 def test_original_runtime_private_session_all_byte_exact(self):
  for name in ('private_session.py','run_native.py','continuation_evidence.py','preservation_projection.py'):self.assertEqual((B/name).read_bytes(),(OLD/name).read_bytes(),name)
 def test_original15_check_asts_and_continuation_equality_exact(self):
  def checks(p):return[ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(p.read_text()))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='check']
  self.assertEqual(checks(B/'private_session.py'),checks(OLD/'private_session.py'))
 def test_separate_namespace_bounded_capture_bubble_no_event_mutation(self):
  s=(B/'KeyboardDiagnostic.js').read_text();self.assertNotIn('qaEvents',s);self.assertIn('entries.length>512',s);self.assertIn('new WeakMap()',s);self.assertIn("observe(event,'capture'),true",s);self.assertIn("observe(event,'bubble'),false",s)
  for forbidden in ('preventDefault(', 'stopPropagation(', '.focus(', 'event.key=', 'event.data=', 'target.value=', 'dispatchEvent(', 'setTimeout(', 'sleep'):
   self.assertNotIn(forbidden,s)
 def test_exact_copied_observer_inline_and_frozen_readonly_property(self):
  self.assertEqual((B/'compose.html').read_text().count((B/'KeyboardDiagnostic.js').read_text()),1)
  s=(B/'cdp_readonly.py').read_text();self.assertEqual(s.count('keyboardDiagnostic:window.qaKeyboardDiagnostic'),1);self.assertIn("p=={'expression':DOM_QUERY,'returnByValue':True}",s)
 def test_actual_qcore_runner_has_no_window_or_gui_application(self):
  s=(B/'keyboard_diagnostic_cpu.cpp').read_text();self.assertIn('QCoreApplication app',s);self.assertNotIn('QGuiApplication',s);self.assertNotIn('QQuickWindow',s)
 def test_build_dependency_bytes_still_exact(self):
  r=json.loads((B/'keyboard-diagnostic-build.json').read_text());self.assertEqual(r['returncode'],0)
  for row in r['dependencies']:self.assertEqual(hashlib.sha256(Path(row['path']).read_bytes()).hexdigest(),row['sha256'],row['path'])
 def test_formal_preceded_listeners_and_actual_runtime(self):
  r=json.loads((B/'dom-keyboard-formal-before-implementation.json').read_text());self.assertEqual(r['result'],'pass');self.assertTrue(r['listenersAndRuntimeStillExactFrozenV17']);self.assertFalse(r['nativeExecuted'])
 def test_old_models_and_product_bytefiles_exact(self):
  for p in [*OLD.glob('*.qnt'),*(OLD/'files-app').rglob('*')]:
   if p.is_file():self.assertEqual((B/p.relative_to(OLD)).read_bytes(),p.read_bytes(),str(p))
if __name__=='__main__':unittest.main()

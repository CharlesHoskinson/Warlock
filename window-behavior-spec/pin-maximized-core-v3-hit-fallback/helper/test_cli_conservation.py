import ast,copy,importlib.util,json,sys,unittest
from pathlib import Path
B=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fresh_pin_helper',B/'helper/pin_helper.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
sys.path.insert(0,str(B))
from test_pin_report_decoder import report,BUILD
class TestCLI(unittest.TestCase):
 def test_all_original_transport_and_process_functions_exact(self):
  old=ast.parse((B/'inverses/helper/pin_helper.py').read_text());new=ast.parse((B/'helper/pin_helper.py').read_text());functions={n.name:n for n in new.body if isinstance(n,ast.FunctionDef)}
  for n in old.body:
   if isinstance(n,ast.FunctionDef) and n.name not in {'validate','result','main'}:
    with self.subTest(function=n.name):self.assertEqual(ast.dump(n,include_attributes=False),ast.dump(functions[n.name],include_attributes=False))
 def test_full_old_result_body_retained(self):
  old=next(n for n in ast.parse((B/'inverses/helper/pin_helper.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='result')
  new=next(n for n in ast.parse((B/'helper/pin_helper.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='_legacy_result');new.name='result'
  self.assertEqual(ast.dump(old),ast.dump(new))
 def test_validate_exact_after_one_new_core_guard_inverse(self):
  old=next(n for n in ast.parse((B/'inverses/helper/pin_helper.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='validate')
  new=next(n for n in ast.parse((B/'helper/pin_helper.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='validate');new.body.pop(0)
  self.assertEqual(ast.dump(old),ast.dump(new))
 def test_main_exact_after_selected_build_argument_inverse(self):
  old=next(n for n in ast.parse((B/'inverses/helper/pin_helper.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='main')
  new=next(n for n in ast.parse((B/'helper/pin_helper.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='main')
  calls=[n for n in ast.walk(new)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='result'];self.assertEqual(len(calls),1);self.assertEqual(len(calls[0].args),3);calls[0].args.pop()
  self.assertEqual(ast.dump(old),ast.dump(new))
 def test_ordinary_schema2_selected_success(self):
  r=report();self.assertTrue(h.result(r,r['captured'],BUILD)['ok'])
 def test_native_max_schema2_selected_success(self):
  r=report(True);self.assertTrue(h.result(r,r['captured'],BUILD)['ok'])
 def test_owned_stale_unpin_schema2_selected_success(self):
  r=report(True,True);self.assertTrue(h.result(r,r['captured'],BUILD)['ok'])
 def test_wrong_core_build_uncertain(self):
  r=report()
  with self.assertRaises(h.Uncertain):h.result(r,r['captured'],'c'*64)
 def test_false_schema1_completion_uncertain(self):
  r=report();del r['schema'];del r['corePolicyBuild']
  with self.assertRaises(h.Uncertain):h.result(r,r['captured'],BUILD)
 def test_original_noaction_refusal_exact(self):
  r=dict(ok=False,phase='validate',reason='old refusal',actionsInvoked=False,possiblePartialOutcome=False);self.assertEqual(h.result(r,report()['captured'],BUILD),r)
 def test_original_partial_uncertainty_observation_exact(self):
  r=dict(ok=False,phase='pin',reason='old partial',actionsInvoked=True,possiblePartialOutcome=True);self.assertEqual(h.result(r,report()['captured'],BUILD),r)
 def test_original_invalid_partial_is_uncertain(self):
  r=dict(ok=False,phase='pin',reason='old partial',actionsInvoked=True,possiblePartialOutcome=False)
  with self.assertRaises(h.Uncertain):h.result(r,report()['captured'],BUILD)
 def test_embedded_decoder_exact(self):
  embedded=ast.parse((B/'helper/pin_helper.py').read_text());allnodes={n.name:n for n in embedded.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
  for node in ast.parse((B/'pin_report_decoder.py').read_text()).body:
   if isinstance(node,(ast.FunctionDef,ast.ClassDef)):
    with self.subTest(name=node.name):self.assertEqual(ast.dump(node),ast.dump(allnodes[node.name]))
if __name__=='__main__':unittest.main()

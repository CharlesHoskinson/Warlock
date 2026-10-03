"""Actual CPU/kernel read-only capture boundary, with an inert mapped fixture.
No compositor, Wayland, GUI input or native pin effect is exercised.
"""
import ast,copy,importlib.util,json,os,subprocess,unittest
from pathlib import Path
B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('capture_candidate',B/'pin_capture.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
spec=importlib.util.spec_from_file_location('root_boundary_tests',B.parent/'pin-helper-v1/test_helper.py');root=importlib.util.module_from_spec(spec);spec.loader.exec_module(root)
class CaptureTests(root.ExecutableTests):
 # Reuse only the exact inert server fixture, not inherited toggle cases.
 def invoke_capture(self,reply_mode='valid',mutate=None,argv_extra=False):
  entry,env,t,config,path,reply=self.fixture()
  entry=entry.with_name('pin_capture.py');entry.write_bytes((B/'pin_capture.py').read_bytes());entry.chmod(0o700)
  config['captureEntry']={'path':str(entry),'sha256':h.digest(entry)}
  pub={'address':t['address'],'stableId':t['stableId'],'pid':t['pid']}
  actual=t if reply_mode=='valid'else dict(t,generation='0')if reply_mode=='invalid-generation'else dict(t,pid=t['pid']+1)
  reply.write_text(json.dumps(actual))
  if mutate:mutate(config)
  path.write_text(json.dumps(config));path.chmod(0o600)
  argv=[str(entry),'capture',json.dumps(pub)]if not argv_extra else['/usr/bin/python3','-I','-S','-B',str(entry),'capture',json.dumps(pub)]
  r=subprocess.run(argv,env=env,capture_output=True,text=True,timeout=4)
  return r,json.loads(r.stdout if r.returncode==0 else r.stderr),config,reply,pub,t
 def test_actual_capture_direct_shebang_exact_token_and_no_writes(self):
  r,e,c,p,pub,t=self.invoke_capture();self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(e['captured'],t);self.assertEqual(e['publicIdentity'],pub);self.assertEqual(e['nativeWrites'],0);self.assertIs(e['nativeCompletionClaimed'],False);self.assertEqual(e['automaticRetries'],0);self.assertTrue(e['transport']['completeServerEOF']);self.assertEqual(Path(str(p)+'.request').read_bytes(),h.command(pub))
 def test_actual_foreign_response_no_action_authority(self):
  r,e,c,p,pub,t=self.invoke_capture('foreign');self.assertEqual(r.returncode,3,r.stderr);self.assertEqual(e['result'],'uncertain');self.assertFalse(e['nativeCompletionClaimed'])
 def test_actual_invalid_generation_no_authority(self):
  r,e,c,p,pub,t=self.invoke_capture('invalid-generation');self.assertEqual(r.returncode,3,r.stderr);self.assertFalse(e['nativeCompletionClaimed'])
 def test_actual_wrong_capture_entry_presend_refusal(self):
  r,e,c,p,pub,t=self.invoke_capture(mutate=lambda c:c['captureEntry'].update(sha256='0'*64));self.assertEqual(r.returncode,1,r.stderr);self.assertNotIn('transport',e);self.assertFalse(Path(str(p)+'.request').exists())
 def test_actual_wrong_capture_kernel_argv_presend_refusal(self):
  r,e,c,p,pub,t=self.invoke_capture(argv_extra=True);self.assertEqual(r.returncode,1,r.stderr);self.assertNotIn('transport',e);self.assertFalse(Path(str(p)+'.request').exists())
 def test_readonly_command_cannot_be_pin_request(self):
  pub=dict(address='0x1234',stableId='abcd',pid=123);self.assertEqual(h.command(pub),b'repl print(hl.plugin.hyprbars.pin_capture({address="0x1234",stableId="abcd",pid=123}))');self.assertNotIn('pin_request',(B/'pin_capture.py').read_text())
 def test_actual_standalone_lua_query_has_exact_string_and_pid(self):
  pub=dict(address='0x1234',stableId='abcd',pid=123)
  command=h.command(pub).decode()[5:]
  script='hl={plugin={hyprbars={pin_capture=function(t) assert(type(t.stableId)=="string" and t.stableId=="abcd" and t.address=="0x1234" and t.pid==123);return "read-only-exact" end}}};'+command
  r=subprocess.run(['/usr/bin/lua','-'],input=script,text=True,capture_output=True,timeout=3);self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(r.stdout.strip(),'read-only-exact')
 def test_typed_public_no_rounding_no_bool(self):
  pub=dict(address='0x1234',stableId='abcd',pid=123)
  for key,bad in [('stableId',True),('stableId',43981),('stableId','10000000000000000'),('stableId','00'),('stableId','ABCD'),('pid',True),('pid',0),('address','0x1234";hl.dispatch("pin")')]:
   with self.subTest(key=key,bad=bad),self.assertRaises(h.Refused):h.public(dict(pub,**{key:bad}))
 def test_original_toggle_entry_exact_root_reviewed_bytes(self):self.assertEqual(h.digest(B/'pin_helper.py'),'30cf295bbc3032b10996e9b6db7c602f6044d38cf73d4eb6ef917e72dd80f0f2')
 def test_original_authority_and_transport_functions_unchanged(self):
  old={n.name:ast.dump(n,include_attributes=False)for n in ast.parse((B/'pin_helper.py').read_text()).body if isinstance(n,ast.FunctionDef)}
  new={n.name:ast.dump(n,include_attributes=False)for n in ast.parse((B/'pin_capture.py').read_text()).body if isinstance(n,ast.FunctionDef)}
  for name in ['digest','process','live','regular','directory','private_path','token','strict_json','read_config','unchanged','source_process','socket_identity','publish']:self.assertEqual(new[name],old[name],name)
  expected=old['validate'].replace("value='entry'","value='captureEntry'").replace("value='toggle'","value='capture'")
  actual=ast.parse((B/'pin_helper.py').read_text());node=next(n for n in actual.body if isinstance(n,ast.FunctionDef)and n.name=='validate')
  node.body=[n for n in node.body if not(isinstance(n,ast.If)and 'Native token compositor differs'in ast.unparse(n))]
  for n in ast.walk(node):
   if isinstance(n,ast.Constant)and n.value=='entry':n.value='captureEntry'
   elif isinstance(n,ast.Constant)and n.value=='toggle':n.value='capture'
  self.assertEqual(new['validate'],ast.dump(node,include_attributes=False))
# Avoid re-running inherited toggle methods: that exact unchanged entry's 32
# CPU/kernel tests remain a separately selected required suite.
for name in list(root.ExecutableTests.__dict__):
 if name.startswith('test_'):setattr(CaptureTests,name,None)
if __name__=='__main__':unittest.main(verbosity=2)

import ast,copy,sys,unittest
from pathlib import Path
from unittest.mock import patch
import audit
B=Path(__file__).resolve().parent;S=B.parent/'toolkit-held-matrix-v10'
class WheelReplay(unittest.TestCase):
 def trace(self,commands):return dict(exitCode=0,normalEOF=True,knownDownTransitionsReleased=True,identity=dict(pid=99999999,start='1'),trace=[dict(pid=99999999,start='1',sentNs=i+1,command=c) for i,c in enumerate(commands)])
 def replay(self,commands,kind='pointer',auth=True):
  c=self.trace(commands);return audit.input_replay(c,kind,dict(identity=c['identity']) if auth else None)
 def test_literal_signed_released_sync_pairs(self):
  self.assertTrue(self.replay(['wheel 1','sync','wheel -1','sync']))
 def test_held_button_refuses_without_fake_release(self):
  self.assertFalse(self.replay(['button 272 1','wheel 1','sync','button 272 0']))
  self.assertTrue(self.replay(['button 272 1','sync','button 272 0','sync','wheel -1','sync']))
 def test_keyboard_and_unauthenticated_refuse(self):
  self.assertFalse(self.replay(['wheel 1','sync'],kind='keyboard'));self.assertFalse(self.replay(['wheel 1','sync'],auth=False))
 def test_malformed_literal_refuses(self):
  for command in ('wheel 0','wheel 2','wheel -2','wheel 1.0','wheel +1','wheel 1 extra','wheel  1',' wheel 1','wheel 1 '):self.assertFalse(self.replay([command,'sync']))
 def test_missing_interposed_or_duplicate_sync_pair_refuses(self):
  for commands in (['wheel 1'],['wheel 1','wheel 1','sync'],['wheel 1','absolute 1 1 10 10','sync'],['wheel 1','button 272 1','sync']):self.assertFalse(self.replay(commands))
 def test_changed_sync_pidstart_order_refuses(self):
  for key,value in (('pid',99999998),('start','2'),('sentNs',1)):
   c=self.trace(['wheel 1','sync']);c['trace'][1][key]=value;self.assertFalse(audit.input_replay(c,'pointer',dict(identity=c['identity'])))
 def test_normal_eof_and_zero_exit_remain_mandatory(self):
  for key,value in (('exitCode',120),('normalEOF',False),('knownDownTransitionsReleased',False)):
   c=self.trace(['wheel 1','sync']);c[key]=value;self.assertFalse(audit.input_replay(c,'pointer',dict(identity=c['identity'])))
 def fixture(self):return audit.js(S/'frozen-inputs.json'),audit.js(S/'attempt-1/qt-wayland/report.json')
 def test_actual_reviewed_binary_source_build_protocol_provenance(self):
  f,v=self.fixture();proof=audit.wheel_proof(S,f,v);self.assertTrue(audit.input_replay(v['cleanup']['pointer'],'pointer',proof))
 def test_changed_binary_or_unknown_producer_argv_refuses(self):
  f,v=self.fixture();original=audit.digest
  with patch('audit.digest',side_effect=lambda p:('0'*64,0o755) if Path(p)==S/'native-pointer-wheel/native-pointer' else original(p)):
   with self.assertRaises(ValueError):audit.wheel_proof(S,f,v)
  row=next(r for r in v['processes'] if r['role']=='pointer');row['argv']=['/usr/bin/true']
  with self.assertRaises(ValueError):audit.wheel_proof(S,f,v)
 def test_missing_cpu_proof_and_changed_parser_or_guard_refuses(self):
  for name in ('wheel-command.h','private-producer-guard.h','native-pointer.c'):
   f,v=self.fixture();original=audit.read
   with patch('audit.read',side_effect=lambda p,limit=134217728:original(p,limit)+b'/* changed */' if Path(p)==S/'native-pointer-wheel'/name else original(p,limit)):
    with self.assertRaises(ValueError):audit.wheel_proof(S,f,v)
  f,v=self.fixture();original=audit.js
  def changed(p):
   value=original(p)
   if Path(p)==S/'native-pointer-wheel/build-report.json':value['cpuProtocolCases']=0
   return value
  with patch('audit.js',side_effect=changed):
   with self.assertRaises(ValueError):audit.wheel_proof(S,f,v)
 def test_original_entire_auditor_reconstructs_exactly(self):
  source=(B/'audit.py').read_text();tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='wheel_proof');source=source.replace(ast.get_source_segment(source,node)+'\n\n','')
  source=source.replace('def input_replay(cleanup,kind,wheel=None):','def input_replay(cleanup,kind):').replace("expected=cleanup['identity'];down=set();last=-1;wheel_pending=False","expected=cleanup['identity'];down=set();last=-1").replace("\n  if wheel_pending and row['command']!='sync':return False\n  if row['command']=='sync':wheel_pending=False",'').replace("  elif parts[0]=='wheel':\n   if kind!='pointer' or row['command'] not in ('wheel 1','wheel -1') or down or wheel is None or wheel['identity']!=expected:return False\n   wheel_pending=True\n",'').replace("return not down and not wheel_pending and bool(cleanup['trace']) and gone(expected)","return not down and bool(cleanup['trace']) and gone(expected)").replace("input_replay(variant['cleanup'][kind],kind,wheel_proof(stage,frozen,variant) if kind=='pointer' and any(row['command'].split()[0]=='wheel' for row in variant['cleanup'][kind]['trace']) else None)","input_replay(variant['cleanup'][kind],kind)")
  self.assertEqual(source,(B.parent/'toolkit-held-terminal-audit-v2/audit.py').read_text())
if __name__=='__main__':unittest.main(verbosity=2)

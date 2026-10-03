from pathlib import Path
import copy,contextlib,importlib.machinery,importlib.util,io,json,sys,tempfile,unittest
B=Path(__file__).resolve().parent
loader=importlib.machinery.SourceFileLoader('staged_snap',str(B/'hypr-snap-groups'));spec=importlib.util.spec_from_loader(loader.name,loader);m=importlib.util.module_from_spec(spec);loader.exec_module(m)
class BackendTests(unittest.TestCase):
 def setUp(self):
  self.state={'snapped':{'0xbeef':{'identity':['0xbeef',123,'fixture','22']}},'groups':[]};self.before=copy.deepcopy(self.state)
 def test_exact_captured_lifetime_removed(self):self.assertTrue(m.forget_closed(self.state,'0xbeef','22',123));self.assertNotIn('0xbeef',self.state['snapped'])
 def test_old_stable_refused(self):self.assertFalse(m.forget_closed(self.state,'0xbeef','11',123));self.assertEqual(self.state,self.before)
 def test_old_pid_refused(self):self.assertFalse(m.forget_closed(self.state,'0xbeef','22',122));self.assertEqual(self.state,self.before)
 def test_wrong_address_refused(self):self.assertFalse(m.forget_closed(self.state,'0xface','22',123));self.assertEqual(self.state,self.before)
 def test_missing_record_refused(self):self.state['snapped']={};self.assertFalse(m.forget_closed(self.state,'0xbeef','22',123))
 def test_malformed_record_refused(self):self.state['snapped']['0xbeef']['identity']=['0xbeef'];self.assertFalse(m.forget_closed(self.state,'0xbeef','22',123))
 def actual_main(self,command,closedStable=None):
  with tempfile.TemporaryDirectory(dir=B) as root:
   m.ROOT=Path(root);m.compositor_instance=lambda:'offline-owned'
   new={'address':'0xbeef','stableId':'22','pid':123,'initialClass':'fixture','class':'fixture','mapped':True,'workspace':{'name':'1'},'monitor':0,'at':[100,250],'size':[460,300]}
   m.clients=lambda:[new]
   def noIPC(*args):raise AssertionError('No IPC allowed')
   m.ctl=noIPC
   state={'version':1,'instance':'offline-owned','snapped':{},'groups':[],'next_id':0}
   m.record(state,[new],'0xbeef','left',normal_size=[460,300]);(m.ROOT/'state.json').write_text(json.dumps(state))
   old=sys.argv;sys.argv=[str(B/'hypr-snap-groups'),command,'0xbeef']+([] if closedStable is None else [closedStable,'123'])
   try:
    with contextlib.redirect_stdout(io.StringIO()) as capture:m.main()
   finally:sys.argv=old
   return json.loads((m.ROOT/'state.json').read_text()),capture.getvalue()
 def test_actual_cli_stale_close_preserves_new(self):
  state,output=self.actual_main('forget-closed','11');self.assertIn('0xbeef',state['snapped']);self.assertFalse(json.loads(output)['removed'])
 def test_actual_cli_exact_close_removes_only_matching(self):
  state,output=self.actual_main('forget-closed','22');self.assertNotIn('0xbeef',state['snapped']);self.assertTrue(json.loads(output)['removed'])
 def test_actual_user_unsnap_semantics_unchanged(self):
  state,output=self.actual_main('unsnap');self.assertNotIn('0xbeef',state['snapped']);self.assertEqual(output,'')
if __name__=='__main__':unittest.main()

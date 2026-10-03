import os,sys,json,copy,importlib.util,unittest
from pathlib import Path
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(B/'host'))
import b_closure as C
sys.path.insert(0,str(B/'controller'))
import minimal_controller as M

class ClosureTests(unittest.TestCase):
 def fixture(self):
  rows=[]
  for i,name in enumerate(C.BASE+['pin-b01-pointer-1']):
   rows.append(dict(name=name,pid=100+i,pgid=100+i,start=str(1000+i),command=[name],registeredExact=True,reaped=True,returncode=0,signals=[],stopError=None))
  client=copy.deepcopy(rows[-1]);before=dict(registered=copy.deepcopy(client),registeredExact=True,pid=client['pid'],returncode=0,gone=True)
  proof=dict(ok=True,error=None,beforeDelegatedClose=True,rawPersisted=True,bindings=[dict(name=client['name'],registered=client)],rows=[before])
  raw=dict(rows=rows,registeredStopOrder=list(reversed([r['name']for r in rows])),closeError=None,originalStopSeconds=4,originalWaitSeconds=4)
  return raw,proof
 def test_exact_normal(self):self.assertTrue(C.classify(*self.fixture()))
 def test_each_actual_client_guard(self):
  for field,value in [('returncode',True),('returncode',-9),('signals',[dict(signal=15,pid=103,sent=True,error=None)]),('reaped',False),('registeredExact',False),('stopError','timeout'),('start','2000'),('pid',True),('pgid',999),('command',['different']),('name','unknown')]:
   with self.subTest(field=field,value=value):
    raw,proof=self.fixture();raw['rows'][-1][field]=value;self.assertFalse(C.classify(raw,proof))
 def test_each_preclose_guard(self):
  for field,value in [('registeredExact',False),('returncode',True),('returncode',-9),('gone',False),('pid',True),('pid',999)]:
   with self.subTest(field=field,value=value):
    raw,proof=self.fixture();proof['rows'][0][field]=value;self.assertFalse(C.classify(raw,proof))
 def test_whole_order_and_base(self):
  for change in range(7):
   raw,proof=self.fixture()
   if change==0:raw['registeredStopOrder'].reverse()
   elif change==1:raw['rows'].append(copy.deepcopy(raw['rows'][-1]))
   elif change==2:raw['rows'][1]['returncode']=-15
   elif change==3:raw['rows'][2]['signals']=[dict(signal=9,pid=102,sent=True,error=None)]
   elif change==4:raw['originalStopSeconds']=4.0
   elif change==5:raw['closeError']='failure'
   else:proof['rawPersisted']=False
   self.assertFalse(C.classify(raw,proof),change)
 def test_named_bus_TERM_is_explicit(self):
  raw,proof=self.fixture();raw['rows'][0]['returncode']=-15
  self.assertFalse(C.classify(raw,proof));raw['rows'][0]['signals']=[dict(signal=15,pid=100,sent=True,error=None)];self.assertTrue(C.classify(raw,proof))
 def test_capture_refusal_latched(self):
  raw,proof=self.fixture();proof['ok']=False;proof['error']='changed source';self.assertFalse(C.classify(raw,proof))
 def test_empty_registry_never_accepts(self):
  raw,proof=self.fixture();raw['rows']=raw['rows'][:3];proof['bindings']=[];proof['rows']=[];self.assertFalse(C.classify(raw,proof))
 def registry_fixture(self):
  output=Path('/exact/native');selected=[dict(name=n,pid=100+i,start=str(200+i),pgid=100+i,command=[n])for i,n in enumerate(C.BASE)]
  argv=[str(C.registry.POINTER),'1600','1000'];registered=dict(name='pin-b01-pointer-1',pid=103,start='203',pgid=103,command=argv,log='/exact/log')
  selected.append(registered);source=dict(path=argv[0],sha256='a'*64,mode=0o755)
  safe={k:False for k in ['sessionLocked','constrained','heldButtons','seatGrab','captured','dnd','dragTarget']};safe.update(exclusiveLayers=0,clickMode=0)
  terminal=dict(pid=103,returncode=0,gone=True,sourceAfter=source,receipt=dict(kind='pointer-eof',allButtonsReleased=True,stdinClosed=True,finalNative=safe))
  row=dict(name=registered['name'],case='B01',kind='pointer',ordinal=1,argv=argv,source=source,registered=registered,normalTerminal=terminal,forced=False)
  return selected,dict(sealed=True,rows=[row]),{argv[0]:source},output
 def test_exact_derived_role(self):self.assertEqual(len(C.derive(*self.registry_fixture())),1)
 def test_derived_closed_world(self):
  for field,value in [('kind','shot'),('case','B13'),('ordinal',True),('ordinal',1.0),('name','arbitrary-extra'),('forced',True),('argv',[str(C.registry.POINTER),'1601','1000'])]:
   with self.subTest(field=field):
    args=list(self.registry_fixture());args[1]['rows'][0][field]=value
    with self.assertRaises(ValueError):C.derive(*args)
 def test_derived_source_and_terminal(self):
  for kind in range(7):
   args=list(self.registry_fixture());row=args[1]['rows'][0]
   if kind==0:row['source']=dict(row['source'],sha256='b'*64)
   elif kind==1:row['normalTerminal']['returncode']=True
   elif kind==2:row['normalTerminal']['receipt']['finalNative']['heldButtons']=True
   elif kind==3:row['registered']=dict(row['registered'],start='999')
   elif kind==4:args[0].append(dict(args[0][-1]))
   elif kind==5:args[1]['sealed']=False
   else:args[1]['rows']=[]
   with self.assertRaises(ValueError):C.derive(*args)
 def test_duplicate_raw_registry(self):
  with self.assertRaises(ValueError):C.strict('{"sealed":true,"sealed":false}')

class ControllerSourceTests(unittest.TestCase):
 def setup_controller(self,response):
  obj=M.MinimalController.__new__(M.MinimalController);calls=[]
  obj.attest=lambda p:None;obj.raw=lambda l,f:f()
  obj.session=type('S',(),{'ctl':lambda _,*args:calls.append(args)or response})()
  obj.helper=type('H',(),{'strict_json':staticmethod(C.strict)})();return obj,calls
 def test_actual_Lua_result_path(self):
  obj,calls=self.setup_controller('{"ok":true,"pass_event":false}')
  obj.setup('prepare','hl.dsp.window.fullscreen({mode="maximized",action="set"})')
  self.assertEqual(calls[0][0],'repl');self.assertIn('local r=hl.dispatch(hl.dsp.window.fullscreen(',calls[0][1]);self.assertIn('type(r.ok)',calls[0][1])
 def test_typed_ACK_never_boolean_alias_or_unknown_dispatcher(self):
  for raw in ['{"ok":1,"pass_event":false}','{"ok":true,"pass_event":0}','{"ok":true,"pass_event":false,"extra":1}','ok','{"ok":false,"pass_event":false}']:
   obj,_=self.setup_controller(raw)
   with self.assertRaises((ValueError,json.JSONDecodeError)):obj.setup('x','hl.dsp.focus({window="address:0x1"})')
  obj,calls=self.setup_controller('{}')
  with self.assertRaises(ValueError):obj.setup('x','setprop address:0x1 allows_input 0')
  self.assertEqual(calls,[])
 def test_canonical_peer_fields(self):
  obj=M.MinimalController.__new__(M.MinimalController);obj.decoder=type('D',(),{'exact':staticmethod(C.exact)})();obj.authority=type('A',(),{'matches':staticmethod(lambda r,c:r.get('address')==c['address'])})()
  rows=[dict(address='0x1',pid=1,stableId='1',pinned=False,floating=False,at=[0,0],size=[1,1],workspace={'id':1},monitor=0,fullscreen=0,fullscreenClient=0),dict(address='0x2',pid=2,stableId='2',pinned=False,floating=True,at=[1,0],size=[1,1],workspace={'id':1},monitor=0,fullscreen=0,fullscreenClient=0)]
  obj.check_peers({'clients':rows},{'clients':list(reversed(rows))},{'address':'0x0'})
  changed=copy.deepcopy(rows);changed[0]['at']=[2,0]
  with self.assertRaises(ValueError):obj.check_peers({'clients':rows},{'clients':changed},{'address':'0x0'})
 def test_nativeMax_immediate_first_transition_refuses(self):
  obj=M.MinimalController.__new__(M.MinimalController);obj.decoder=type('D',(),{'exact':staticmethod(C.exact)})()
  keys=['logicalBox','visualBox','restoreLogicalBox','restoreVisualBox','restoreTarget','restoreLayoutTarget','restoreSpace','restoreOrigin','target','space','workspace','output']
  normal={k:'same'for k in keys};normal.update(internalMode=0,clientMode=0,floating=False,restoreValid=True,restoreGeneration='1',restoreFloating=False,restoreLayoutHandled=True,restoreManaged=True)
  maximum=dict(normal,internalMode=1);calls=[];snapshots=iter([{'body':normal},{'body':maximum}])
  obj.capture=lambda actor:{'address':'0x1'};obj.snapshot=lambda c:next(snapshots);obj.focus=lambda *a:None;obj.setup=lambda *a:None;obj.wait=lambda label,f:f()
  def first(*args):
   calls.append(args);corrupt=dict(maximum,clientMode=2);return {'after':{'pinned':True}},{'owned':{'body':corrupt}}
  obj.pin_titlebar=first
  with self.assertRaisesRegex(ValueError,'immediately after genuine pin'):obj.native_max_case('B04',{})
  self.assertEqual(len(calls),1,'must reject before inverse transition could hide a first-pin defect')
 def test_import_has_no_launch(self):
  import ast
  tree=ast.parse((B/'controller/minimal_controller.py').read_text())
  self.assertFalse(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in {'Popen','ctl','launch','run_first_phase','load'}for statement in tree.body if not isinstance(statement,(ast.ClassDef,ast.FunctionDef))for n in ast.walk(statement)))
if __name__=='__main__':unittest.main(verbosity=2)

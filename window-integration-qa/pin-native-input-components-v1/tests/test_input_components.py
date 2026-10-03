"""CPU observations execute new actual methods; no native reachability claim."""
import ast,copy,importlib.util,json,sys,unittest
from pathlib import Path
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent.parent
P=Path('/home/hoskinson/window-integration-qa/pin-max-native-campaign-b-v4')
sys.path.insert(0,str(B/'host'));import b_closure as C
sys.path.insert(0,str(B/'controller'));import block_controller as M

class Components(unittest.TestCase):
 def adapter(self,active='owner'):
  o=M.BlockController.__new__(M.BlockController)
  o.decoder=type('D',(),{'exact':staticmethod(C.exact)})()
  o.authority=type('A',(),{'matches':staticmethod(lambda v,t:C.exact(v,t)),'input_safe':staticmethod(lambda n:None)})()
  tokens={n:dict(address='0x1'if n=='owner'else'0x2',pid=101,stableId=n,compositorPid=99,compositorStart='123',session='exact')for n in ['owner','peer']}
  bodies={}
  for n in tokens:
   r={k:'same'for k in M.CONTEXT};r.update(owner=tokens[n],mapped=True,hidden=False,noFocus=False,priorityFocus=False,pinned=n=='owner',floating=False,internalMode=0,clientMode=0,group='0x0',groupMembers=[],acceptsInput=n==active)
   bodies[n]=r
  workspace=dict(id=11,monitorID=0,tiledLayout='monocle',windows=2,hasfullscreen=False,lastwindow=tokens[active]['address'])
  o.raw=lambda l,f:f();o.session=type('S',(),{'data':lambda _,name:[workspace]})()
  o.capture=lambda actor,n='owner':copy.deepcopy(tokens[n])
  o.snapshot=lambda t,*a:dict(body=copy.deepcopy(bodies[t['stableId']]),hitOwner=copy.deepcopy(tokens[active]))
  o.public=lambda actor,n:dict(workspace=dict(id=11),monitor=0)
  o.old_probe=lambda name:dict(nativeFocus=copy.deepcopy(tokens[active]))if name=='state'else dict(keyboardOwner=copy.deepcopy(tokens[active]),keyboardSurfacePresent=True,keyboardResourcePresent=True)
  return o,tokens,bodies,workspace
 def test_actual_native_scope_and_unchanged_owned_projection(self):
  o,t,b,w=self.adapter();before=o.scope({},t,'owner');o.conserve(before,copy.deepcopy(before))
  changed=copy.deepcopy(before);changed['owned']['peer']['body']['restoreSpace']='replaced'
  with self.assertRaises(ValueError):o.conserve(before,changed)
  self.assertIs(before['numericReasonObserved'],False)
  self.assertIs(before['renderedOwnerVisibleProved'],False)
 def test_workspace_typed_actual_algorithm_guard(self):
  for k,v in [('id',True),('id',11.0),('monitorID',False),('monitorID',1),('windows',2.0),('windows',True),('tiledLayout','scrolling'),('hasfullscreen',0),('hasfullscreen',True),('lastwindow','0x3')]:
   with self.subTest(k=k,v=v):
    o,t,b,w=self.adapter();w[k]=v
    with self.assertRaises(ValueError):o.actual_workspace(11,'monocle',2,t['owner'])
 def test_current_member_mode_group_and_input_refusals(self):
  for member in ['owner','peer']:
   for k,v in [('mapped',False),('hidden',True),('noFocus',True),('floating',True),('internalMode',False),('internalMode',1),('clientMode',0.0),('clientMode',1),('group','0x1'),('groupMembers',['0x1']),('pinned',member!='owner'),('acceptsInput',member!='owner'),('acceptsInput',1 if member=='owner'else 0),('space','replaced'),('workspace','replaced'),('output','replaced')]:
    with self.subTest(member=member,k=k,v=v):
     o,t,b,w=self.adapter();b[member][k]=v
     with self.assertRaises(ValueError):o.scope({},t,'owner')
 def test_full_root_member_tokens_and_post_confirmation_refused(self):
  for phase in ['initial','confirm']:
   for field in ['address','pid','stableId','compositorPid','compositorStart','session']:
    with self.subTest(phase=phase,field=field):
     o,t,b,w=self.adapter();calls=[];original=o.capture
     def capture(actor,name='owner'):
      r=original(actor,name);calls.append(name)
      if name=='owner'and ((phase=='initial'and len(calls)==1)or(phase=='confirm'and len(calls)==3)):r[field]='replacement'
      return r
     o.capture=capture
     with self.assertRaises(ValueError):o.scope({},t,'owner')
 def test_current_core_seat_and_public_scope_refusals(self):
  for kind in ['core','seat','surface','resource','publicworkspace','publicmonitor']:
   with self.subTest(kind=kind):
    o,t,b,w=self.adapter();old=o.old_probe
    if kind.startswith('public'):
     o.public=lambda a,n:dict(workspace=dict(id=True if kind=='publicworkspace'else 11),monitor=False if kind=='publicmonitor'else 0)
    else:
     def probe(name):
      r=old(name)
      if kind=='core'and name=='state':r['nativeFocus']=t['peer']
      if name=='keyboard_state':
       if kind=='seat':r['keyboardOwner']=t['peer']
       if kind=='surface':r['keyboardSurfacePresent']=False
       if kind=='resource':r['keyboardResourcePresent']=False
      return r
     o.old_probe=probe
    with self.assertRaises(ValueError):o.scope({},t,'owner')
 def case_adapter(self,fault=None):
  o,t,b,w=self.adapter();log=[];current={'active':'owner','events':[],'clicked':False}
  o.focus=lambda actor,token:current.update(active=token['stableId'])
  o.retained_tiled=lambda *a:dict(sourceObserved='CPU adapter only')
  original_scope=o.scope
  def scope(actor,tokens,active):
   for n in b:b[n]['acceptsInput']=n==current['active']
   w['lastwindow']=t[current['active']]['address']
   log.append('scope-'+active)
   if fault=='blocked-input'and active=='peer':b['owner']['acceptsInput']=True
   if fault=='clear-input'and active=='owner'and current['clicked']:b['owner']['acceptsInput']=False
   return original_scope(actor,tokens,active)
  o.scope=scope
  def probe(name):
   if name=='events':return copy.deepcopy(current['events'])
   if name=='state':return dict(nativeFocus=t[current['active']])
   return dict(keyboardOwner=t[current['active']],keyboardSurfacePresent=True,keyboardResourcePresent=True)
  o.old_probe=probe
  o.snapshot=lambda token,*a:dict(body=copy.deepcopy(b[token['stableId']]),hitOwner=t['peer'])
  o.wait=lambda label,fn,seconds=5:fn()
  o.qt_point=lambda *a:[100,100];o.qt_box=lambda *a:[90,90,20,20]
  o.point_inside=lambda point,box:fault!='no-overlap'
  o.fixture_state=lambda a:dict(windows={'owner':dict(clicks=1 if fault=='owner-callback'and current['clicked']else 0),'peer':dict(clicks=1 if current['clicked']else 0)})
  def launch(*a):log.append('pointer-launch');return object(),{}
  o.registry=type('R',(),{'launch':staticmethod(launch)})()
  o.move_pointer=lambda *a,**kw:log.append('move')
  def write(pointer,text):
   code,state=map(int,text.split()[1:]);current['events'].append(dict(button=code,buttonState=state,native={'hitOwner':t['owner'if fault=='revived-hit'else'peer']}))
   if state==0:current['clicked']=True
  o.pointer_write=write;o.close_pointer=lambda p:log.append('pointer-close')
  def unpin(*a):log.append('genuine-unpin');return dict(after=dict(pinned=False)),dict(owned=dict(body=dict(acceptsInput=True)))
  o.pin_keyboard=unpin
  return o,log
 def test_actual_method_balanced_input_and_clear_before_unpin(self):
  o,log=self.case_adapter();result=o.monocle_case({})
  self.assertEqual(log.count('pointer-launch'),1);self.assertEqual(log.count('pointer-close'),1)
  self.assertLess(log.index('pointer-close'),log.index('genuine-unpin'))
  self.assertEqual(log[log.index('genuine-unpin')-1],'scope-owner')
  self.assertEqual([r['buttonState']for r in result['actual']['buttons']],[1,0]);self.assertIs(result['fullDesignCaseAccepted'],False)
 def test_refuse_before_pointer_for_invalid_scope_or_real_overlap(self):
  for fault in ['blocked-input','no-overlap']:
   o,log=self.case_adapter(fault)
   with self.assertRaises(ValueError):o.monocle_case({})
   self.assertNotIn('pointer-launch',log);self.assertNotIn('genuine-unpin',log)
 def test_nonrevival_and_native_clear_refuse_before_unpin(self):
  for fault in ['revived-hit','owner-callback','clear-input']:
   o,log=self.case_adapter(fault)
   with self.assertRaises(ValueError):o.monocle_case({})
   self.assertIn('pointer-close',log);self.assertNotIn('genuine-unpin',log)
 def test_independent_B12_uses_exact_inherited_method(self):
  o=M.BlockController.__new__(M.BlockController);calls=[];o.setup=lambda *a:calls.append(('setup',a));o.attest=lambda *a:None;o.launch_actor=lambda c:dict(case=c)
  o.exclusion_case=lambda c,a:calls.append(('exclusion',c))or dict(case=c);o.monocle_case=lambda *a:self.fail('B12 must not require B11');o.retire_actor=lambda a:calls.append(('retire',a));o.trace=[];o.persist=lambda:None;o.registry=type('R',(),{'seal_before_host_close':lambda _:None})()
  r=o.run_components('B12');self.assertEqual(r['componentCases'],['B12']);self.assertIs(r['originalTwelveCaseIncrementAccepted'],False)
  self.assertIn(('exclusion','B12'),calls)
 def test_base_source_and_nineteen_tests_exact(self):
  for name in ['controller/minimal_controller.py','tests/test_controller_packet.py','producer-registry/registry.py','host/candidate_host.py','observer/decode_observation.py']:
   self.assertEqual((B/name).read_bytes(),(P/name).read_bytes(),name)
  self.assertIs(M.BlockController.exclusion_case,M.MinimalController.exclusion_case)
 def test_exact_component_selectors_and_import_no_effect(self):
  self.assertEqual(M.CASES,{'B11':('B11',),'B12':('B12',),'B11+B12':('B11','B12')})
  tree=ast.parse((B/'controller/block_controller.py').read_bytes())
  self.assertFalse(any(isinstance(n,ast.Call)for stmt in tree.body if not isinstance(stmt,(ast.ClassDef,ast.FunctionDef))for n in ast.walk(stmt)))
  compile((B/'run_native.py').read_bytes(),str(B/'run_native.py'),'exec')

if __name__=='__main__':unittest.main(verbosity=2)

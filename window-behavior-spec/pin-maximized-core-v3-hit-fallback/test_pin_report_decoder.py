import copy,json,unittest
from pin_report_decoder import decode,Refusal,BOOLS
BUILD='a'*64

def report(native=False,stale=False):
 before={'address':'0x101','stableId':'9','pid':123,'epoch':'1','generation':'2','session':'private_session','incarnation':'b'*32,'internalMode':1 if native else 0,'clientMode':1 if native else 0,'capability':1,'restoreGeneration':'3' if native else '0','target':'0x201' if native else '0x0','layoutTarget':'0x202' if native else '0x0','space':'0x203' if native else '0x0','workspace':'0x204','monitor':'0x205','geometry':['10','20','600','400'],'restoreGeometry':['20','30','420','350','21','31','418','348'] if native else ['0']*8}
 before.update({k:False for k in BOOLS});before.update(live=True,normal=True,pinned=native,fullscreen=native,floating=not native,nativeAdmission=native and not stale,ownedUnpinReady=native,restoreKnown=native and not stale,restoreOrigin=native,restoreManaged=native)
 after=copy.deepcopy(before);after['pinned']=not native
 if native:after['restoreOrigin']=False;after['ownedUnpinReady']=False
 token={k:before[k]for k in ['address','stableId','pid','session','incarnation','epoch','generation']};token.update(compositorPid=456,compositorStart='789')
 return dict(schema=2,corePolicyBuild=BUILD,ok=True,phase='complete',reason='',actionsInvoked=True,possiblePartialOutcome=False,captured=token,before=before,after=after,desiredPinned=not native,backend=dict(ok=True,message='',level='',code=''))

def raw(r):return json.dumps(r,allow_nan=False).encode()
class TestDecoder(unittest.TestCase):
 def refused(self,r):
  with self.assertRaises(Refusal):decode(raw(r),BUILD)
 def test_ordinary_original_float_pin_projection(self):self.assertTrue(decode(raw(report()),BUILD)['ok'])
 def test_native_max_unpin_preserves_return(self):self.assertTrue(decode(raw(report(True)),BUILD)['ok'])
 def test_stale_owned_unpin_has_no_return_authority(self):self.assertTrue(decode(raw(report(True,True)),BUILD)['ok'])
 def test_stale_exclusive_owned_unpin_preserves_mode(self):
  r=report(True,True)
  for name in ['before','after']:r[name]['internalMode']=2;r[name]['clientMode']=2
  self.assertTrue(decode(raw(r),BUILD)['ok'])
 def test_all_boolean_aliases(self):
  for section in ['before','after']:
   for key in BOOLS:
    for alias in [0,1,0.0,1.0,'true',None]:
     with self.subTest(section=section,key=key,alias=alias):r=report(True);r[section][key]=alias;self.refused(r)
 def test_integer_bool_float_aliases(self):
  for section in ['before','after','captured']:
   for key in (['pid','compositorPid'] if section=='captured' else ['pid','internalMode','clientMode','capability']):
    for alias in [True,False,1.0,'1']:
     with self.subTest(section=section,key=key,alias=alias):r=report(True);r[section][key]=alias;self.refused(r)
 def test_schema_alias(self):
  for alias in [True,2.0,'2',1,3]:r=report();r['schema']=alias;self.refused(r)
 def test_full_snapshot_schema(self):
  for section in ['before','after']:
   for key in list(report(True)[section]):r=report(True);del r[section][key];self.refused(r)
 def test_extra_fields(self):
  for section in ['', 'before','after','backend','captured']:
   r=report();(r[section]if section else r)['unexpected']=False;self.refused(r)
 def test_token_lifetime_equality(self):
  for key in ['address','stableId','pid','epoch','generation','session','incarnation']:
   r=report(True);r['after'][key]=124 if key=='pid' else ('0x102'if key=='address'else'4');self.refused(r)
 def test_native_current_context_equality(self):
  for key in ['target','layoutTarget','space','workspace','monitor']:
   r=report(True);r['after'][key]='0x987';self.refused(r)
 def test_geometry_changed_refused(self):
  for key in ['geometry','restoreGeometry']:
   r=report(True);r['after'][key][0]='21';self.refused(r)
 def test_nonfinite_or_numeric_geometry(self):
  for alias in [True,1.0,'NaN','Infinity','1e9999','01']:
   r=report(True);r['before']['geometry'][0]=alias;self.refused(r)
 def test_generation_bounds(self):
  for alias in [True,1,'01','-1',str(2**64)]:r=report(True);r['before']['restoreGeneration']=alias;self.refused(r)
 def test_native_missing_restore_refused(self):r=report(True);r['before']['restoreKnown']=False;self.refused(r)
 def test_changed_native_modes_refused(self):r=report(True);r['after']['internalMode']=0;self.refused(r)
 def test_false_complete_refused(self):r=report();r['backend']['ok']=False;self.refused(r)
 def test_partial_flag_truth(self):r=report();r['possiblePartialOutcome']=True;self.refused(r)
 def test_wrong_build(self):
  with self.assertRaises(Refusal):decode(raw(report()),'c'*64)
 def test_duplicate_key(self):
  with self.assertRaises(Refusal):decode(b'{"schema":2,"schema":2}',BUILD)
 def test_absent_capture_refused_on_success(self):r=report();r['captured']=None;self.refused(r)
 def test_closed_refused(self):r=report(True);r['after']['live']=False;self.refused(r)
 def test_unmapped_scope_refused(self):r=report(True);r['after']['normal']=False;self.refused(r)
 def test_same_intent_refused(self):r=report(True);r['desiredPinned']=True;self.refused(r)
 def test_stale_cannot_pin(self):r=report(True,True);r['before']['pinned']=False;r['desiredPinned']=True;self.refused(r)
 def test_ordinary_does_not_fabricate_float(self):r=report();r['after']['floating']=False;self.refused(r)
 def test_refusal_keeps_partial_raw_observations(self):
  r=report(True);r.update(ok=False,phase='pin',possiblePartialOutcome=True);r['after']['live']=False
  self.assertFalse(decode(raw(r),BUILD)['ok'])

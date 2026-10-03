"""CPU-only schema adversaries. Synthetic bytes confer no native reachability credit."""
import copy,importlib.util,json,unittest
from pathlib import Path
P=Path(__file__).resolve().parent.parent/'src/decode_observation.py'
sp=importlib.util.spec_from_file_location('observer_decoder',P);d=importlib.util.module_from_spec(sp);sp.loader.exec_module(d)
ROOT=dict(compositorPid=5000,compositorPgid=5000,compositorStart='100',session='qa_100')
OWNER=dict(address='0x1234',stableId='a1',pid=6000)
def sample(query=False):
 b=dict(owner=OWNER.copy(),mapped=True,hidden=False,acceptsInput=True,noFocus=False,priorityFocus=False,pinned=True,floating=False,internalMode=1,clientMode=1,fullscreenHandler='0xa0',target='0xb0',space='0xc0',workspace='0xd0',output='0xe0',logicalBox=['0','0','1600','1000'],visualBox=['0','0','1600','1000'],restoreValid=True,restoreGeneration='7',restoreLogicalBox=['10','20','800','600'],restoreVisualBox=['10','20','800','600'],restoreFloating=False,restoreLayoutHandled=False,restoreTarget='0xb0',restoreLayoutTarget='0xb0',restoreSpace='0xc0',restoreOrigin=True,restoreManaged=True,ownedUnpinReady=True,group='0x0',groupMembers=[],cursor=['12','24'],coreFocus=OWNER.copy(),scroll=None,transfer=None)
 return dict(schema=1,queryKind='windowAtStimulus'if query else 'metadata',queryProperties=19 if query else None,ignoreOwner=None,hitOwner=OWNER.copy()if query else None,corePolicyBuild=d.POLICY,**ROOT,sequence='1',observedNs='1000',ok=True,error=None,body=b,postBody=copy.deepcopy(b))
def scrolling():
 s=dict(owner='0xf0',controller='0xf1',selectedData='0xf2',selectedColumn='0xf3',offset='123.25',direction=0,columns=[dict(column='0xf3',width='0.5',rows=[dict(data='0xf2',target='0xb0',owner=OWNER.copy(),size='1',layoutBox=['1','2','3','4'])])])
 r=sample();r['body']['scroll']=s;r['postBody']=copy.deepcopy(r['body']);return r
def transferred(accepted=True):
 t=dict(operation='9',generation='8',accepted=accepted,actualModesKnown=accepted,beforeInternal=1,beforeClient=1,actualInternal=1 if accepted else 0,actualClient=1 if accepted else 0,target='0xb0'if accepted else '0x0',space='0xc0'if accepted else '0x0',workspace='0xd0'if accepted else '0x0',output='0xe0'if accepted else '0x0',reason='accepted'if accepted else 'handler-refused')
 r=sample();r['body']['transfer']=t;r['postBody']=copy.deepcopy(r['body']);return r
def encoded(row):return json.dumps(row,separators=(',',':')).encode()
def decode(row,mask=None,ignore=False):return d.decode(encoded(row),ROOT,OWNER,mask,ignore)
class DecodeFaults(unittest.TestCase):
 def refuse(self,r,mask=None,ignore=False):
  with self.assertRaises(ValueError):decode(r,mask,ignore)
 def mutate_body(self,key,value):
  r=sample();r['body'][key]=value;r['postBody']=copy.deepcopy(r['body']);return r
 def test_pure_metadata_positive(self):self.assertEqual(decode(sample())['queryKind'],'metadata')
 def test_hit_stimulus_positive(self):self.assertEqual(decode(sample(True),0)['hitOwner'],OWNER)
 def test_all_fixed_masks_and_ignore_positive(self):
  for i,mask in enumerate(d.MASKS):
   r=sample(True);r['queryProperties']=mask;r['ignoreOwner']=OWNER.copy();self.assertEqual(decode(r,i,True)['queryProperties'],mask)
 def test_scrolling_complete_current_positive(self):self.assertEqual(decode(scrolling())['body']['scroll']['offset'],'123.25')
 def test_transfer_accepted_positive(self):self.assertTrue(decode(transferred())['body']['transfer']['accepted'])
 def test_transfer_refused_retained_non_success(self):self.assertFalse(decode(transferred(False))['body']['transfer']['accepted'])
 def test_primitive_bool_int_float_aliases(self):
  for key in ['schema','compositorPid','compositorPgid']:
   for value in [True,1.0]:
    r=sample();r[key]=value;self.refuse(r)
  for key in ['ok']:
   for value in [1,1.0]:
    r=sample();r[key]=value;self.refuse(r)
 def test_all_body_boolean_aliases(self):
  for key in ['mapped','hidden','acceptsInput','noFocus','priorityFocus','pinned','floating','restoreValid','restoreFloating','restoreLayoutHandled','restoreOrigin','restoreManaged','ownedUnpinReady']:
   for value in [1,0,1.0,0.0]:self.refuse(self.mutate_body(key,value))
 def test_native_mode_scalar_aliases(self):
  for key in ['internalMode','clientMode']:
   for value in [True,1.0,-1,4]:self.refuse(self.mutate_body(key,value))
 def test_root_lifetime_session_replacement(self):
  for key,value in [('compositorPid',5001),('compositorPgid',5001),('compositorStart','101'),('session','qa_101')]:
   r=sample();r[key]=value;self.refuse(r)
 def test_selected_public_replacement(self):
  for key,value in [('address','0x1235'),('stableId','a2'),('pid',6001)]:
   r=sample();r['body']['owner'][key]=value;r['postBody']=copy.deepcopy(r['body']);self.refuse(r)
 def test_source_policy_replacement(self):
  r=sample();r['corePolicyBuild']='0'*64;self.refuse(r)
 def test_partial_and_changed_post_observation(self):
  r=sample();r['postBody']=None;self.refuse(r)
  r=sample();r['postBody']['logicalBox'][0]='1';self.refuse(r)
  r=sample();r['postBody']['pinned']=False;self.refuse(r)
 def test_refusal_with_partial_before_not_usable(self):
  r=sample();r.update(ok=False,error='owning scope changed',postBody=None,sequence=None);self.refuse(r)
 def test_unknown_extra_and_missing_fields(self):
  r=sample();r['newAuthority']=True;self.refuse(r)
  r=sample();del r['body']['restoreValid'];r['postBody']=copy.deepcopy(r['body']);self.refuse(r)
 def test_duplicate_raw_json_keys(self):
  raw=encoded(sample()).replace(b'"schema":1',b'"schema":1,"schema":1')
  with self.assertRaises(ValueError):d.decode(raw,ROOT,OWNER)
 def test_non_json_constants_and_bad_utf8(self):
  for raw in [encoded(sample()).replace(b'"schema":1',b'"schema":NaN'),b'\xff']:
   with self.assertRaises(ValueError):d.decode(raw,ROOT,OWNER)
 def test_response_size_bound(self):
  with self.assertRaises(ValueError):d.decode(b' '*131073,ROOT,OWNER)
 def test_metadata_cannot_smuggle_hit_stimulus(self):
  r=sample();r['queryProperties']=19;self.refuse(r)
  r=sample();r['hitOwner']=OWNER.copy();self.refuse(r)
  self.refuse(sample(),None,True)
 def test_hit_kind_and_mask_are_request_bound(self):
  self.refuse(sample(True))
  r=sample(True);r['queryProperties']=27;self.refuse(r,0)
  r=sample(True);r['queryProperties']=19.0;self.refuse(r,0)
 def test_ignore_cannot_select_replacement(self):
  r=sample(True);r['ignoreOwner']={**OWNER,'pid':6001};self.refuse(r,0,True)
 def test_pointer_canonical_and_positive_scope(self):
  for value in ['0xb00g','0x00b0','0xB0','0x0',1]:self.refuse(self.mutate_body('target',value))
 def test_generation_and_sequence_overflow(self):
  for v in ['01','-1',str(2**64),'0',1,True]:
   r=sample();r['sequence']=v;self.refuse(r)
   self.refuse(self.mutate_body('restoreGeneration',v))
 def test_scalar_numeric_alias_nonfinite_and_shape(self):
  for value in [[0,'0','10','10'],['NaN','0','10','10'],['0','0','Infinity','10'],['0','0','10'],['0','0','1'*65,'10']]:self.refuse(self.mutate_body('logicalBox',value))
 def test_restore_scope_replacement(self):
  for key in ['restoreLayoutTarget','restoreSpace']:self.refuse(self.mutate_body(key,'0xffff'))
 def test_group_inventory_cannot_hide_reuse(self):
  r=sample();r['body'].update(group='0xf9',groupMembers=[OWNER.copy(),OWNER.copy()]);r['postBody']=copy.deepcopy(r['body']);self.refuse(r)
  self.refuse(self.mutate_body('group','0xf9'))
 def test_scroll_selected_row_scope_and_duplicate(self):
  for field,value in [('selectedData','0xfa'),('selectedColumn','0xfb')]:
   r=scrolling();r['body']['scroll'][field]=value;r['postBody']=copy.deepcopy(r['body']);self.refuse(r)
  r=scrolling();r['body']['scroll']['columns'][0]['rows']*=2;r['postBody']=copy.deepcopy(r['body']);self.refuse(r)
 def test_scroll_complete_bounds_and_scalar_types(self):
  r=scrolling();r['body']['scroll']['columns']*=65;r['postBody']=copy.deepcopy(r['body']);self.refuse(r)
  for field,value in [('direction',True),('offset',1.0)]:
   r=scrolling();r['body']['scroll'][field]=value;r['postBody']=copy.deepcopy(r['body']);self.refuse(r)
 def test_transfer_cannot_bless_unknown_or_typed_aliases(self):
  for field,value in [('actualModesKnown',False),('accepted',1),('actualInternal',1.0),('operation','0')]:
   r=transferred();r['body']['transfer'][field]=value;r['postBody']=copy.deepcopy(r['body']);self.refuse(r)
if __name__=='__main__':unittest.main(verbosity=2)

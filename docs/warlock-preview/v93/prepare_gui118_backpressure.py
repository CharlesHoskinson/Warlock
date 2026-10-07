"""Retain the original48 backpressure controls and add readonly custody checks."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v118')
s=(root/'qa/persistent-policy-backpressure-check.py').read_text().replace('persistent-policy-backpressure-check','readonly-policy-backpressure-check')
s=s.replace('child=None;steps=[];checks=0','child=None;steps=[];checks=0;readonly=0')
old="  row=call({'op':'invoke','input':json.dumps({'kind':kind,'value':value},separators=(',',':'))});check(row['ok'] and row['code']==0,'Original owned invocation succeeds');return row['projection']"
new="""  global readonly
  row=call({'op':'invoke','input':json.dumps({'kind':kind,'value':value},separators=(',',':'))});check(row['ok'] and row['code']==0,'Original owned invocation succeeds')
  visual=call({'op':'visual'})
  if row['projection']['realm']['closed'] or not row['projection']['realm']['controlled']:
   assert visual=={'ok':False,'code':6,'held':True},'Closed/absent authority refuses readonly copy'
  else:
   assert visual=={'ok':True,'code':0,'held':True,'projection':row['projection']['visuals']},'Latest visual-only projection survives original input/deferred intent'
  readonly+=1
  return row['projection']"""
assert s.count(old)==1;s=s.replace(old,new)
old="check(send('status')==before,'Exact retained policy remains after WOULD_BLOCK')"
new=old+";visual=call({'op':'visual'});assert visual=={'ok':True,'code':0,'held':True,'projection':before['visuals']},'WOULD_BLOCK preserves exact committed visual copy';readonly+=1"
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace("checks=checks,syntheticNativeIssuedFacts", "checks=checks,readonlyProjectionChecks=readonly,syntheticNativeIssuedFacts")
s=s.replace("'scope':'Actual sanitizer", "'scope':'Readonly queries compare exact latest visual-only projection after every original successful call and all three ordinary WOULD_BLOCK refusals. Actual sanitizer")
ast.parse(s);target=root/'qa/readonly-policy-backpressure-check.py';assert not target.exists();target.write_text(s);print(target)

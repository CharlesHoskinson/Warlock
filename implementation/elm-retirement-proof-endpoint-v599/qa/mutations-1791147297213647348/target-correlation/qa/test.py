import pathlib,sys,json,copy,time,hashlib,dataclasses
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapter'))
from grant_endpoint import GrantEndpoint,NativeBinding,RetirementProof
from effect_endpoint import Endpoint as EffectEndpoint
from endpoint import Refused,ValidatedNativeRefusal
OUT=ROOT/'qa'/('test-'+str(time.time_ns()));OUT.mkdir()
report={'passed':False,'scope':'Immutable native596 wire decoder replay plus explicitly synthetic transport/fault controls; no new SO_PEERCRED/native qualification','checks':[]}
def check(name,ok):
 report['checks'].append({'name':name,'passed':bool(ok)})
 assert ok,name
class Synthetic(GrantEndpoint):
 def __init__(self,bound,response,hook=None):
  self.bound=copy.deepcopy(bound);self.response=copy.deepcopy(response);self._grant_watermarks={};self.hook=hook;self.calls=[]
 def request(self,payload):
  self.calls.append(copy.deepcopy(payload))
  if self.hook:self.hook(self,payload)
  if isinstance(self.response,Exception):raise self.response
  return copy.deepcopy(self.response)
def refusal(name,fn,endpoint=None,call_count=None):
 before=copy.deepcopy(endpoint._grant_watermarks) if endpoint else None
 try:fn()
 except Refused:
  check(name,True)
  if endpoint:check(name+'-watermark-unchanged',before==endpoint._grant_watermarks)
  if call_count is not None:check(name+'-transport-count',len(endpoint.calls)==call_count)
 else:raise AssertionError(name+' accepted')
try:
 source=ROOT/'qa/fixtures/native596-report.json';native=json.loads(source.read_text())
 check('producer42-checks-passed',native['passed'] and len(native['checks'])==42 and all(x['passed'] for x in native['checks']))
 fixtures=[]
 for index,row in enumerate(native['wire']):
  req=row['request'].get('request');resp=row['reply'].get('response')
  if req and resp and resp.get('kind')=='binding-retirement':
   fixtures.append({'sourceIndex':index,'peer':row['peer'],'request':req,'reply':resp})
 check('immutable-native-proof-fixtures-exist',len(fixtures)>=5)
 (OUT/'native-wire-fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
 for case in fixtures:
  req=case['request'];resp=case['reply'];ep=Synthetic(req['binding'],resp)
  method=ep.retire if req['kind']=='binding-retire-request' else ep.observe
  proof=method(req['requestId'],req['queriedBinding'])
  check('native-wire-'+str(case['sourceIndex']),proof.as_dict()==resp and ep.calls==[req])
  check('native-release-policy-'+str(case['sourceIndex']),proof.allows_release==(resp['grantState']=='Retired'))
 base=next(x for x in fixtures if x['reply']['operation']=='retire')
 current=base['request']['binding'];target=base['request']['queriedBinding'];rid=base['request']['requestId'];reply=base['reply']
 def new(response=reply,hook=None):return Synthetic(current,response,hook)
 check('legacy-methods-inherited',all(getattr(GrantEndpoint,n) is getattr(EffectEndpoint,n) for n in ['request','hello','snapshot','scene_facts','context','effect']))
 ep=new();p=ep.retire(rid,target)
 try:p.grant_state='Registered'
 except dataclasses.FrozenInstanceError:check('immutable-proof',True)
 else:raise AssertionError('mutable proof')
 wire=p.as_dict();wire['binding']['frontend']='99'
 check('proof-export-copy',p.binding.frontend==current['frontend'])
 refusal('duplicate-sequence',lambda:ep.retire(rid,target),ep)
 lower=copy.deepcopy(reply);lower['sequence']=str(int(reply['sequence'])-1);ep.response=lower
 refusal('lower-sequence',lambda:ep.retire(rid,target),ep)
 ep.bound=copy.deepcopy(current);ep.bound['frontend']=str(int(current['frontend'])+1);updated=copy.deepcopy(reply);updated['binding']=copy.deepcopy(ep.bound);ep.response=updated
 refusal('frontend-change-does-not-reset-sequence',lambda:ep.retire(rid,target),ep)
 for field in reply:
  bad=copy.deepcopy(reply);del bad[field];ep=new(bad)
  refusal('missing-'+field,lambda:ep.retire(rid,target),ep)
 bad=copy.deepcopy(reply);bad['extra']=0;ep=new(bad);refusal('extra-reply-field',lambda:ep.retire(rid,target),ep)
 for field,values in [('protocolVersion',[True,3.0,0,'3']),('retirementProtocol',[True,1.0,0,'1']),('kind',['attached',False]),('operation',['observe','other',False]),('grantState',['Registered','Future','Unknown','retired',None,False,{}])]:
  for i,value in enumerate(values):
   bad=copy.deepcopy(reply);bad[field]=value;ep=new(bad)
   refusal('bad-'+field+'-'+str(i),lambda:ep.retire(rid,target),ep)
 counters=[False,True,1,1.0,None,'0','01','+1','-1',' 1','1 ','18446744073709551616','1\n']
 for field in ['requestId','sequence']:
  for i,value in enumerate(counters):
   bad=copy.deepcopy(reply);bad[field]=value;ep=new(bad)
   refusal('bad-'+field+'-counter-'+str(i),lambda:ep.retire(rid,target),ep)
 for group in ['binding','queriedBinding']:
  for field in ['lifetime','session','frontend']:
   for i,value in enumerate(counters):
    bad=copy.deepcopy(reply);bad[group][field]=value;ep=new(bad)
    refusal('bad-'+group+'-'+field+'-'+str(i),lambda:ep.retire(rid,target),ep)
   bad=copy.deepcopy(reply);bad[group][field]=str(int(bad[group][field])+1);ep=new(bad)
   refusal('mismatched-'+group+'-'+field,lambda:ep.retire(rid,target),ep)
  for shape in [None,[],{'lifetime':'1','session':'1'},{**reply[group],'extra':'1'}]:
   bad=copy.deepcopy(reply);bad[group]=shape;ep=new(bad)
   refusal('bad-'+group+'-shape-'+str(shape),lambda:ep.retire(rid,target),ep)
 bad=copy.deepcopy(reply);bad['requestId']=str(int(rid)+1);ep=new(bad)
 refusal('mismatched-request-id',lambda:ep.retire(rid,target),ep)
 for state in ['Registered','Future','Retired']:
  obs=copy.deepcopy(reply);obs['operation']='observe';obs['grantState']=state;ep=new(obs);p=ep.observe(rid,target)
  check('observe-'+state,p.grant_state==state and p.allows_release==(state=='Retired'))
 ep=new();ep.bound=None;refusal('unattached',lambda:ep.retire(rid,target),ep,0)
 for value in counters:
  ep=new();refusal('invalid-input-request-'+repr(value),lambda:ep.retire(value,target),ep,0)
 for group in ['caller','target']:
  for field in ['lifetime','session','frontend']:
   for i,value in enumerate(counters):
    ep=new();queried=copy.deepcopy(target)
    (ep.bound if group=='caller' else queried)[field]=value
    refusal('invalid-input-'+group+'-'+field+'-'+str(i),lambda:ep.retire(rid,queried),ep,0)
 foreign=copy.deepcopy(target);foreign['lifetime']=str(int(current['lifetime'])+1);ep=new()
 refusal('foreign-input-lifetime',lambda:ep.observe(rid,foreign),ep,0)
 ep=new();refusal('self-retirement-local-refusal',lambda:ep.retire(rid,current),ep,0)
 def replace_binding(ep,payload):ep.bound={**ep.bound,'frontend':str(int(ep.bound['frontend'])+1)}
 ep=new(hook=replace_binding);refusal('inflight-binding-replacement',lambda:ep.retire(rid,target),ep)
 def mutate_binding(ep,payload):ep.bound['frontend']=str(int(ep.bound['frontend'])+1)
 ep=new(hook=mutate_binding);refusal('inflight-binding-in-place-change',lambda:ep.retire(rid,target),ep)
 original=copy.deepcopy(target)
 ep=new(hook=lambda ep,payload:target.update(frontend='99'));proof=ep.retire(rid,target)
 check('caller-input-mutation-does-not-rebind-request',proof.queried_binding.as_dict()==original and ep.calls[0]['queriedBinding']==original);target=original
 ep=new(ValidatedNativeRefusal('retirement-future-grant'))
 refusal('native-refusal-not-proof',lambda:ep.retire(rid,target),ep)
 # Actual uint64 max is accepted where legal, with no float conversion.
 high=copy.deepcopy(reply);high['requestId']='18446744073709551615';high['sequence']='18446744073709551615';ep=new(high)
 check('uint64-max-exact',ep.retire(high['requestId'],target).sequence==high['sequence'])
 refusal('max-sequence-no-wrap',lambda:ep.retire(high['requestId'],target),ep)
 ep=new();ep._grant_watermarks={str(i):1 for i in range(1,17)}
 refusal('lifetime-history-bound-before-transport',lambda:ep.retire(rid,target),ep,0)
 report.update(passed=True,nativeWireFixtureCount=len(fixtures),nativeSourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),endpointSHA256=hashlib.sha256((ROOT/'adapter/grant_endpoint.py').read_bytes()).hexdigest(),syntheticTransportQualified=False,nativeAcceptance=False)
except Exception as e:report['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])

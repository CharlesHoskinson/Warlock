"""Production opt-in codec regressions; native/transport execution is separate."""
import copy,json,pathlib,random,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'adapter'))
from effect_endpoint import Endpoint
from endpoint import Refused,ValidatedNativeRefusal
BINDING={'lifetime':'1','session':'2','frontend':'3'}
INTENT={'request':'7','generation':'9','incarnation':'4','operation':'restore','context':{'lifetime':'1','epoch':'3','output':'5','revision':'6'}}
DEADLINE='18446744073709551615'
CAPS={'observe':True,'effects':True,'minimizedState':True,'effectProtocol':1,'operations':['minimize','restore','activate'],'canonicalScene':False,'taskbarProjectionProtocol':1,'effectInvalidationProtocol':1}
checks=[]
def check(value,name):
 if not value:raise AssertionError(name)
 checks.append(name)
def refused(call,name):
 try:call()
 except Refused:checks.append(name);return
 raise AssertionError(name+' accepted')
class Client(Endpoint):
 def __init__(self):
  self.bound=copy.deepcopy(BINDING);self.calls=[];self.patch=None;self.status='Committed';self.prepare_status=None;self.after=None;self.pid=4242;self.instance='nativeqa'
 def request(self,payload):
  self.calls.append(copy.deepcopy(payload));kind=payload['kind']
  identity={'protocolVersion':3,'cancellationProtocol':1,'effectProtocol':1,'binding':copy.deepcopy(payload.get('binding',self.bound)),'intent':copy.deepcopy(payload.get('intent',INTENT)),'preparedId':payload.get('preparedId','41'),'deadlineMonotonicNs':payload.get('deadlineMonotonicNs',DEADLINE)}
  if kind=='hello':
   r={'protocolVersion':3,'kind':'attached','binding':{**BINDING,'frontend':'4'},'compositor':{'pid':self.pid,'instance':self.instance,'coreHash':'recorded-core'},'capabilities':copy.deepcopy(CAPS)}
  elif kind=='effect-cancellation-negotiate':
   r={'protocolVersion':3,'kind':'effect-cancellation-capabilities','binding':copy.deepcopy(payload['binding']),'requestId':payload['requestId'],'cancellationProtocol':1,'effectProtocol':1,'operations':['restore'],'maxPreparedPerSession':1,'maxPreparedGlobal':64,'deadlineClock':'CLOCK_MONOTONIC'}
  elif kind=='effect-prepare' and self.prepare_status is None:r={**identity,'kind':'effect-prepared'}
  elif kind=='effect-decision-ack':r={**identity,'kind':'effect-decision-acknowledged'}
  elif kind=='window-effect':r={'protocolVersion':3,'kind':'effect-outcome','effectProtocol':1,'binding':copy.deepcopy(payload['binding']),'intent':copy.deepcopy(payload['intent']),'status':'Committed','reason':'applied','revision':'11','outputGeneration':'5'}
  else:
   status=self.prepare_status if kind=='effect-prepare' else self.status
   r={**identity,'kind':'effect-outcome','status':status,'reason':{'Committed':'applied','Refused':'dependency-mismatch','Unknown':'effect-unproven','Cancelled':'cancelled-before-commit'}[status],'revision':'11','outputGeneration':'5'}
  if self.patch:r=self.patch(copy.deepcopy(r))
  if self.after:self.after(self)
  return r

def negotiated():
 c=Client();c.cancellation_negotiate('1');return c

def prepared():
 c=negotiated();return c,c.prepare_effect(copy.deepcopy(INTENT),DEADLINE)

def patch(name,value):return lambda r:{**r,name:copy.deepcopy(value)}

c=Client();refused(lambda:c.prepare_effect(INTENT,DEADLINE),'prepare requires negotiated current grant');check(not c.calls,'no transport before negotiation')
c=negotiated();check(c.calls==[{'protocolVersion':3,'kind':'effect-cancellation-negotiate','binding':BINDING,'requestId':'1','cancellationProtocol':1}],'separate exact negotiation preserves legacy hello')
original=copy.deepcopy(INTENT);p=c.prepare_effect(original,DEADLINE);check(original==INTENT,'prepare preserves caller intent');check(c.calls[-1]=={'protocolVersion':3,'kind':'effect-prepare','cancellationProtocol':1,'effectProtocol':1,'binding':BINDING,'intent':INTENT,'deadlineMonotonicNs':DEADLINE},'prepare preserves full immutable key and original deadline')
for method,kind in [('commit_effect','effect-commit'),('cancel_effect','effect-cancel'),('query_effect_decision','effect-decision-request')]:
 for status in ['Committed','Refused','Unknown','Cancelled']:
  c,p=prepared();c.status=status;old=copy.deepcopy(p);r=getattr(c,method)(p);check(r['status']==status and p==old,method+' accepts exact '+status+' without mutating descriptor')
  check(c.calls[-1]=={'protocolVersion':3,'kind':kind,'cancellationProtocol':1,'effectProtocol':1,'binding':BINDING,'intent':INTENT,'preparedId':'41','deadlineMonotonicNs':DEADLINE},method+' preserves exact identity and deadline for '+status)
for status in ['Committed','Refused','Cancelled']:
 c,p=prepared();c.status=status;terminal=c.query_effect_decision(p);ack=c.ack_effect_decision(terminal);check(ack['kind']=='effect-decision-acknowledged' and c.calls[-1]['kind']=='effect-decision-ack','ACK exact terminal '+status)
c,p=prepared();c.status='Unknown';unknown=c.query_effect_decision(p);before=len(c.calls);refused(lambda:c.ack_effect_decision(unknown),'Unknown is never locally acknowledgeable');refused(lambda:c.ack_effect_decision(p),'Prepared is never locally acknowledgeable');check(len(c.calls)==before,'unsafe ACK refuses before transport')
for status in ['Committed','Refused','Unknown','Cancelled']:
 c=negotiated();c.prepare_status=status;check(c.prepare_effect(INTENT,DEADLINE)['status']==status,'duplicate prepare can recover native '+status+' without executing')
check(all(r['kind']!='window-effect' for r in c.calls),'opt-in never falls back to legacy execution')
c,p=prepared();terminal=c.query_effect_decision(p);c.status='Refused';refused(lambda:c.query_effect_decision(p),'known terminal cannot change on native contradiction');c.status='Committed';check(c.query_effect_decision(p)==terminal,'rejected contradictory reply preserves known terminal')
c=negotiated();c.bound['frontend']='4';before=len(c.calls);refused(lambda:c.prepare_effect({**INTENT,'context':{**INTENT['context'],'epoch':'4'}},DEADLINE),'mutating bound alias cannot transfer negotiation');check(len(c.calls)==before,'mutated alias sends no request')
for value in ['0','01','-1','18446744073709551616',1,True,None,{},[]]:
 c=negotiated();before=len(c.calls);refused(lambda:c.prepare_effect(INTENT,value),'invalid original deadline '+repr(value));check(len(c.calls)==before,'invalid deadline never sent '+repr(value))
 c=Client();refused(lambda:c.cancellation_negotiate(value),'invalid negotiation request '+repr(value));check(not c.calls,'invalid negotiation never sent '+repr(value))
for change in [{'operation':'activate'},{'operation':'minimize'},{'extra':1},{'request':'0'},{'context':{**INTENT['context'],'epoch':'4'}},{'context':{**INTENT['context'],'lifetime':'2'}},{'context':{**INTENT['context'],'revision':True}}]:
 c=negotiated();before=len(c.calls);refused(lambda:c.prepare_effect({**copy.deepcopy(INTENT),**change},DEADLINE),'invalid intent '+repr(change));check(len(c.calls)==before,'invalid intent not submitted '+repr(change))
for name,value in [('kind','attached'),('cancellationProtocol',True),('effectProtocol',2),('maxPreparedGlobal',63),('maxPreparedGlobal',True),('maxPreparedPerSession',2),('operations',['restore','activate']),('deadlineClock','CLOCK_REALTIME'),('requestId','2'),('binding',{**BINDING,'frontend':'4'}),('extra',1)]:
 c=Client();c.patch=patch(name,value);refused(lambda:c.cancellation_negotiate('1'),'bad capability '+name+repr(value));before=len(c.calls);refused(lambda:c.prepare_effect(INTENT,DEADLINE),'failed negotiation supplies no grant '+name+repr(value));check(len(c.calls)==before,'bad capability cannot submit '+name+repr(value))
mutations=[('kind','receipt'),('cancellationProtocol',True),('effectProtocol',2),('binding',{**BINDING,'frontend':'4'}),('intent',{**INTENT,'incarnation':'99'}),('intent',{**INTENT,'context':{**INTENT['context'],'revision':'99'}}),('preparedId','42'),('deadlineMonotonicNs','99'),('status','Pending'),('reason','bad\nreason'),('reason','x'*129),('reason','bad\x00reason'),('revision','0'),('revision',True),('outputGeneration','18446744073709551616'),('extra',1)]
seed=0xCA11CE01;rng=random.Random(seed)
for index in range(200):
 c,p=prepared();c.status=rng.choice(['Committed','Refused','Unknown','Cancelled']);name,value=mutations[rng.randrange(len(mutations))];c.patch=patch(name,value);before=len(c.calls);method=rng.choice(['commit_effect','cancel_effect','query_effect_decision']);refused(lambda:getattr(c,method)(p),'seeded malformed/correlation reply '+str(index));check(len(c.calls)==before+1 and c.calls[-1]['kind']!='window-effect','seeded negative reaches only intended transport '+str(index))
c,p=prepared();c.bound={**BINDING,'frontend':'4'};before=len(c.calls);refused(lambda:c.commit_effect(p),'changed frontend retires negotiation');check(len(c.calls)==before,'changed frontend cannot submit')
c,p=prepared();c.after=lambda x:setattr(x,'bound',{**BINDING,'frontend':'4'});refused(lambda:c.commit_effect(p),'binding change during transport cannot deliver old result')
c,p=prepared();c.hello();before=len(c.calls);refused(lambda:c.prepare_effect({**INTENT,'context':{**INTENT['context'],'epoch':'4'}},DEADLINE),'successful hello resets cancellation negotiation');check(len(c.calls)==before,'new hello does not inherit negotiation')
c=Client();legacy=copy.deepcopy(INTENT);legacy['operation']='activate';check(c.effect(legacy)['status']=='Committed' and c.calls[-1]['kind']=='window-effect','legacy effect remains independent of opt-in negotiation')
print(json.dumps({'passed':True,'checks':len(checks),'seed':hex(seed),'generatedReplyCases':200,'nativeAcceptance':False,'transportAuthenticationProved':False,'scope':'Production strict cancellation client codec with explicit native response doubles; actual authenticated native fixture and durable daemon/UI routing remain separate.'}))

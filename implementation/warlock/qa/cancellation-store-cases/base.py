from fixture import *
with tempfile.TemporaryDirectory(prefix='warlock-v7-test-') as temporary:
 root=pathlib.Path(temporary);legacy=DeliveryLedger(root,'durabilityqa','1');where=legacy.path;legacy.close()
 old=(where/'ledger-v6.json').read_bytes();oldsha=hashlib.sha256(old).hexdigest()
 with open_store(root,'durabilityqa','1') as store:
  envelope=json.loads((store.path/'ledger-v7.json').read_text())
  check(envelope['schema']==7 and envelope['predecessorV6SHA256']==oldsha,'V7 pins exact immutable V6 predecessor')
  check((where/'ledger-v6.json').read_bytes()==old,'V7 initialization preserves V6 bytes')
  refused(lambda:validate({**admission(intent()),'status':'Cancelled'}),'legacy schema never gains uncertified Cancelled')
  key,rec,native,wire=prepared(store,intent())
  saved=store.cancellation_reserve(BOUND,intent(),DEADLINE);check(saved['submitPrepare'] is False,'duplicate reservation never authorizes prepare replay')
  outcome=terminal(store,key,rec,native,wire)
  check(outcome['status']=='Cancelled' and not store.ledger.snapshot()['entries'],'known cancellation removes only certified local reservation without Refused conversion')
  check((where/'ledger-v6.json').read_bytes()==old,'cancellation writes never mutate frozen V6')
  host_cached_retirement(store,key) # Explicit newly required durable host-cache prerequisite.
  # Exact old Pending reappearance cannot resurrect it or erase a newer intent.
  pending(store,intent());new=intent('2');pending(store,new)
  check(store.begin(BOUND,new,1) is True,'new legacy admission follows certified cancellation under shared target guard')
  store.cancellation_finish(key)
  current=store.ledger.snapshot();check(current['latest']['intent']==new and any(r['intent']==new for r in current['entries']),'idempotent old finish preserves newer latest and reservation')
  check(not (store.path/'admissions-v1'/(storage_key(rec)+'.json')).exists(),'exact old Pending reappearance is durably removed before ordinary import')
  check((store.path/'admissions-v1'/(storage_key(admission(new))+'.json')).exists(),'different full key pending is not retired by target similarity')
 with open_store(root,'durabilityqa','1') as reopened:
  records=reopened.cancellation_snapshot({**BOUND,'frontend':'4'})
  check(any(r['admission']==rec and r['certificate'] is not None for r in records),'restart retains certificate on its original immutable binding')
  check((where/'ledger-v6.json').read_bytes()==old,'restart does not invoke a mutable V6 constructor')
 # Semantically equal predecessor drift must still be detected, never rebaselined.
 (where/'ledger-v6.json').write_bytes(old+b' ')
 refused(lambda:RecoveryStore(root,'durabilityqa','1',cancellation=True),'V6 predecessor byte drift fails closed')

# Validation refusals may poison a workflow; independent fixtures never assume
# a rejected operation authorizes further mutation in that same instance.
for case in ['missing','deadline','ack','dict','attempt','overwritten-attempt']:
 with tempfile.TemporaryDirectory(prefix='warlock-v7-negative-') as temporary:
  with open_store(pathlib.Path(temporary),'durabilityqa','1') as store:
   if case=='missing':
    refused(lambda:store.cancellation_reserve(BOUND,intent(),DEADLINE),'missing actual shared C admission refuses')
    continue
   key,rec,native,wire=prepared(store,intent())
   if case=='deadline':
    refused(lambda:store.cancellation_reserve(BOUND,intent(),'99'),'original deadline cannot be replaced')
   elif case=='ack':
    refused(lambda:store.cancellation_ack_pending(key),'Prepared cannot acknowledge or release native custody')
   elif case=='dict':
    refused(lambda:store.cancellation_observe(key,copy.deepcopy(wire)),'frontend dictionary cannot become typed native evidence')
   else:
    store.cancellation_attempt(key,'commit')
    # Native request has not been sent at this cut; it is still Prepared.
    if case=='overwritten-attempt':store.cancellation_attempt(key,'cancel')
    reply=native.query_effect_decision(wire)
    store.cancellation_observe(key,_native_cancellation_evidence(rec,DEADLINE,wire['preparedId'],reply,phase='established'))
    refused(lambda:store.cancellation_attempt(key,'commit'),'queried Prepared and overwritten last operation never reset consumed commit permission '+case)

print(json.dumps({'passed':True,'checks':len(checks),'nativeAcceptance':False,'powerLossProved':False,'scope':'Actual shared admission files and V7 filesystem/client transitions with explicit native response doubles; no C/Elm/native resource or physical input claim.'}))

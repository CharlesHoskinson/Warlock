from fixture import *
for case in ['explicit-commit','native-owned-cancel','corrupt-prepared','corrupt-committed']:
 with tempfile.TemporaryDirectory(prefix='warlock-v7-provenance-positive-') as temporary:
  root=pathlib.Path(temporary);store=open_store(root,'provenancepositiveqa','1')
  key,rec,native,wire=prepared(store,intent())
  if case=='explicit-commit':
   result=terminal(store,key,rec,native,wire,'commit')
   check(result['status']=='Committed','durably attempted commit remains accepted and ACKable')
  elif case=='native-owned-cancel':
   # Correlated terminal native certificate may originate outside local Cancel.
   response=native.cancel_effect(wire)
   saved=store.cancellation_observe(key,_native_cancellation_evidence(rec,DEADLINE,wire['preparedId'],response,phase='established'))
   check(saved['certificate']['response']['status']=='Cancelled' and saved['attemptedKinds']==['prepare'],'native-certified cancellation does not require local Cancel marker')
   store.cancellation_finish(key);certificate=store.cancellation_ack_pending(key)
   check(certificate==response,'native-owned cancellation retires durably before ACK permission')
  else:
   if case=='corrupt-committed':terminal(store,key,rec,native,wire,'commit')
   path=store.path/'ledger-v7.json';state=json.loads(path.read_text());record=state['cancellations'][0]
   record['attemptedKinds']=[] if case=='corrupt-prepared' else ['prepare'];record['lastOperation']=None if case=='corrupt-prepared' else 'prepare';record['commitAttempted']=False
   path.write_bytes(encoded(state));store.close();store=None
   refused(lambda:RecoveryStore(root,'provenancepositiveqa','1',cancellation=True),case+' persisted missing attempt marker refuses reopen')
  if store is not None:store.close()
print(json.dumps({'passed':True,'checks':len(checks),'nativeAcceptance':False,'scope':'Actual store valid explicitCommit/native-ownedCancel controls and persisted missing-marker corruption refusal; native response doubles only.'}))

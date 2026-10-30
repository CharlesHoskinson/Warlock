from fixture import *
fixed='--expect-fixed' in sys.argv
observations=[]
for case in ['unattempted-prepare','unattempted-commit']:
 with tempfile.TemporaryDirectory(prefix='warlock-v7-provenance-') as temporary:
  with open_store(pathlib.Path(temporary),'provenanceqa','1') as store:
   if case=='unattempted-prepare':
    rec=cancellation_pending(store,intent());reserved=store.cancellation_reserve(BOUND,intent(),DEADLINE);key=reserved['record']['key']
    native=Native();native.cancellation_negotiate('1');wire=native.prepare_effect(intent(),DEADLINE)
    proof=_native_cancellation_evidence(rec,DEADLINE,None,wire,phase='initial')
   else:
    key,rec,native,wire=prepared(store,intent())
    response=native.commit_effect(wire)
    proof=_native_cancellation_evidence(rec,DEADLINE,wire['preparedId'],response,phase='established')
   before=(store.path/'ledger-v7.json').read_bytes()
   try:result=store.cancellation_observe(key,proof);accepted=True
   except Refused:accepted=False
   if fixed:check(not accepted and (store.path/'ledger-v7.json').read_bytes()==before,case+' refuses before persistence')
   else:check(accepted,case+' expected private baseline gap reproduced')
   observations.append({'case':case,'acceptedWithoutDurableAttempt':accepted})
print(json.dumps({'passed':True,'expectedDefectReproduced':not fixed,'observations':observations,'scope':'Actual store with strictly correlated native-response doubles supplied out of order; no actual native mutation/transport/daemon bug claimed.'}))

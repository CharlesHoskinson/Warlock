from fixture import *
with tempfile.TemporaryDirectory(prefix='warlock-v7-typed-restart-') as temporary:
 root=pathlib.Path(temporary)
 with open_store(root,'typedrestartqa','1') as store:
  key,rec,native,wire=prepared(store,intent())
  original=store.cancellation_snapshot(BOUND)[0]
  frozen=(store.path/'ledger-v6.json').read_bytes()
  calls=copy.deepcopy(native.calls)
 with RecoveryStore(root,'typedrestartqa','1',cancellation=True) as reopened:
  state=reopened.ledger.snapshot()
  check(state['entries'][0]['status']=='Unknown' and state['latest']['status']=='Unknown','typed restart also exposes Unknown legacy custody')
  record=reopened.cancellation_snapshot(BOUND)[0]
  check(record==original and record['admission']==rec and record['admission']['status']=='Pending','typed key/stage/prepared evidence immutable across custody normalization')
  check((reopened.path/'ledger-v6.json').read_bytes()==frozen,'typed restart leaves predecessor frozen')
  check(native.calls==calls,'restart does not invoke strict client or a native effect')
  refused(lambda:reopened.cancellation_attempt(key,'commit'),'disk record is not current live attachment')
  reopened.cancellation_attach(BOUND)
  refused(lambda:reopened.cancellation_attempt(key,'commit'),'same binding reattach does not reacquire historical mutation permission')
  frames=reopened.cancellation_recovery_frames({**BOUND,'frontend':'4'})
  check(len(frames)==1 and frames[0]['kind']=='host-cancellation-recovery' and frames[0]['recoveryState']=='Unknown' and frames[0]['executionAuthorized'] is False and frames[0]['record']==original,'historical Prepared report preserves original evidence without effect authority')
print(json.dumps({'passed':True,'checks':len(checks),'nativeAcceptance':False,'scope':'Actual typed restart custody normalization, immutable keys, no replay and informational reporting with strict response double only.'}))

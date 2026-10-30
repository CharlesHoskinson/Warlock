from fixture import *
INTENT=intent()
results=[]
for cancellation in [False,True]:
 with tempfile.TemporaryDirectory(prefix='warlock-legacy-restart-') as temp:
  root=pathlib.Path(temp)
  with RecoveryStore(root,'restartqa','1',cancellation=cancellation) as store:
   row={'schema':2,'effectProtocol':1,'binding':copy.deepcopy(BOUND),'intent':copy.deepcopy(INTENT),'status':'Pending'}
   with store.ledger.host_guard() as directory:
    fd=os.open(storage_key(row)+'.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
    try:
     data=encoded(row);offset=0
     while offset<len(data):offset+=os.write(fd,data[offset:])
     os.fsync(fd)
    finally:os.close(fd)
    os.fsync(directory)
   assert store.begin(BOUND,INTENT,1) is True
   before=store.ledger.snapshot();assert before['latest']['status']=='Pending'
   frozen=(store.path/'ledger-v6.json').read_bytes() if cancellation else None
  with RecoveryStore(root,'restartqa','1',cancellation=cancellation) as reopened:
   after=reopened.ledger.snapshot();read=reopened.read('intent.json')
   results.append({'cancellation':cancellation,'entries':[x['status'] for x in after['entries']],'latest':after['latest']['status'],'readIntent':read['status'],'intentUnchanged':after['latest']['intent']==INTENT,'watermarksUnchanged':before['watermarks']==after['watermarks'],'frozenV6Unchanged':not cancellation or (reopened.path/'ledger-v6.json').read_bytes()==frozen})
expected='Unknown' if '--expect-fixed' in sys.argv else 'Pending'
assert results[0]['entries']==['Unknown'] and results[0]['latest']=='Unknown' and results[0]['readIntent']=='Unknown',results
assert results[1]['entries']==[expected] and results[1]['latest']==expected and results[1]['readIntent']==expected,results
assert all(x['intentUnchanged'] and x['watermarksUnchanged'] and x['frozenV6Unchanged'] for x in results),results
print(json.dumps({'passed':True,'defectReproduced':expected=='Pending','results':results,'scope':'Actual ordinary legacy begin/reopen, no native execution or typed cancellation mutation.'}))

from fixture import *
fixed=True
results=[]
for explicit in [False,True]:
 with tempfile.TemporaryDirectory(prefix='warlock-v7-downgrade-') as temporary:
  root=pathlib.Path(temporary)
  with open_store(root,'downgradeqa','1') as store:
   key,original,native,wire=prepared(store,intent());where=store.path
   typed=store.cancellation_snapshot(BOUND)[0];frozen=(where/'ledger-v6.json').read_bytes()
  before={str(p.relative_to(where)):p.read_bytes() for p in where.rglob('*') if p.is_file()}
  opened=False
  try:
   candidate=RecoveryStore(root,'downgradeqa','1',**({'cancellation':False} if explicit else {}));opened=True;candidate.close()
  except Refused:pass
  after={str(p.relative_to(where)):p.read_bytes() for p in where.rglob('*') if p.is_file()}
  unchanged=(where/'ledger-v6.json').read_bytes()==frozen
  if fixed:
   check(not opened and before==after,'legacy default/false refuses before any downgrade data mutation '+str(explicit))
   with RecoveryStore(root,'downgradeqa','1',cancellation=True) as reopened:
    check(reopened.cancellation_snapshot(BOUND)[0]==typed and (where/'ledger-v6.json').read_bytes()==frozen,'V7 still opens with original typed custody/predecessor '+str(explicit))
  else:
   check(opened and not unchanged,'expected RED legacy default/false mutates frozen V6 '+str(explicit))
   refused(lambda:RecoveryStore(root,'downgradeqa','1',cancellation=True),'expected RED later V7 refuses its changed predecessor '+str(explicit))
  results.append({'explicitFalse':explicit,'downgradeOpened':opened,'frozenV6Unchanged':unchanged})

import stat
from recovery_journal import Journal

def data(where):
 result={}
 for path in where.rglob('*'):
  mode=path.lstat().st_mode;name=str(path.relative_to(where))
  if stat.S_ISREG(mode):result[name]=('file',path.read_bytes())
  elif stat.S_ISLNK(mode):result[name]=('link',os.readlink(path))
  elif stat.S_ISDIR(mode):result[name]=('directory',)
  else:result[name]=('special',stat.S_IFMT(mode))
 return result
for case in ['file-only','marker-only','symlink','directory','fifo']:
 with tempfile.TemporaryDirectory(prefix='warlock-v7-owner-partial-') as temporary:
  root=pathlib.Path(temporary)
  with RecoveryStore(root,'partialqa','1') as store:where=store.path
  target=where/('ledger-v7.initialized' if case=='marker-only' else 'ledger-v7.json')
  if case in ['file-only','marker-only']:target.write_bytes(b'{}');target.chmod(0o600)
  elif case=='symlink':target.symlink_to('absent-target')
  elif case=='directory':target.mkdir(mode=0o700)
  else:os.mkfifo(target,0o600)
  before=data(where)
  refused(lambda:RecoveryStore(root,'partialqa','1'),'legacy default refuses V7 presence '+case)
  check(data(where)==before,'partial V7 ownership remains byte/type exact '+case)
  refused(lambda:Journal(root,'partialqa','1'),'direct Journal cannot bypass ownership '+case)
  check(data(where)==before,'direct rejection before legacy migration '+case)
with tempfile.TemporaryDirectory(prefix='warlock-v7-clean-legacy-') as temporary:
 root=pathlib.Path(temporary)
 for kw in [{},{'cancellation':False}]:
  with RecoveryStore(root,'cleanlegacyqa','1',**kw) as store:
   check(type(store.ledger).__name__=='DeliveryLedger' and not (store.path/'ledger-v7.json').exists(),'clean legacy mode remains usable '+repr(kw))
 with open_store(root,'otherlifeqa','1') as store:prepared(store,intent())
 with RecoveryStore(root,'otherlifeqa','2') as store:
  check(store.ledger.target['lifetime']=='2' and not (store.path/'ledger-v7.json').exists(),'V7 ownership guard is scoped to exact namespace/lifetime')

print(json.dumps({'passed':True,'checks':len(checks),'nativeAcceptance':False,'scope':'Actual V7 downgrade/partial-marker ownership checks, byte preservation and clean/default/lifetime controls; no real native operation.'}))

"""Actual revisioned store and authenticated adapter, including ambiguous save."""
import json,os,pathlib,sys,tempfile
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from motion_preferences import Store,snapshot
from endpoint import Refused
from catalog_transport import CatalogTransport

checks={}
def check(name,condition):
 checks[name]=bool(condition);assert condition,name
def rejects(name,operation):
 try:operation()
 except (Refused,OSError,ValueError):check(name,True)
 else:check(name,False)
with tempfile.TemporaryDirectory(prefix='warlock-live-motion-') as directory:
 state=pathlib.Path(directory);store=Store(state);file=store.path/'motion.json'
 default=store.read();check('missingStoreFollowsSystemWithoutWriting',default=={'schema':1,'revision':'1','override':None} and not file.exists())
 saved,value=store.save({**default,'override':'reduced'});check('atomicReducedOverride',saved=='Saved' and value['revision']=='2' and file.stat().st_mode&0o777==0o600)
 check('restartReadsSavedOverride',Store(state).read()==value)
 check('staleRevisionRefusedWithoutRewrite',store.save({**default,'override':'full'})[0]=='Refused' and store.read()==value)
 check('unchangedValueRefused',store.save(value)[0]=='Refused')
 saved,reset=store.save({**value,'override':None});check('resetRemovesExplicitOverride',saved=='Saved' and reset['override'] is None and reset['revision']=='3')
 for name,invalid in [('futureSchema',{**reset,'schema':2}),('zeroRevision',{**reset,'revision':'0'}),('unknownOverride',{**reset,'override':'fast'}),('frontEndPath',{**reset,'path':'/tmp/foreign'})]:rejects(name,lambda invalid=invalid:snapshot(invalid))
 future=b'{"schema":2,"revision":"8","override":"reduced"}';file.write_bytes(future)
 rejects('futureReadRefused',store.read);rejects('futureSaveRefused',lambda:store.save(reset));check('futureVersionBytesPreserved',file.read_bytes()==future)
 file.write_text('{"schema":1,"revision":"3","override":null,"override":"full"}')
 rejects('duplicateFieldsRejected',store.read)
 file.write_text(json.dumps(reset));file.chmod(0o644);rejects('publicFileRejected',store.read);file.chmod(0o600)
 file.unlink();foreign=state/'foreign';foreign.write_text(json.dumps(reset));file.symlink_to(foreign);rejects('symlinkRejected',store.read);file.unlink()
 file.write_text(json.dumps(reset));file.chmod(0o600)
 fsync=os.fsync
 def fail_directory(fd):
  import stat
  if stat.S_ISDIR(os.fstat(fd).st_mode):raise OSError('directory fsync lost after rename')
  fsync(fd)
 with patch('motion_preferences.os.fsync',side_effect=fail_directory):result=store.save({**reset,'override':'full'})
 check('postRenameFailureIsUnknown',result==('Unknown',None))
 committed=store.read();check('explicitReadReconcilesAmbiguousCommit',committed['revision']=='4' and committed['override']=='full')
 check('noTemporaryFilesRemain',not list(store.path.glob('motion.*.tmp')))
 class Client:
  bound={'lifetime':'1','session':'1','frontend':'1'}
  def verify_process(self):pass
  def verify_paths(self):pass
 with patch.dict(os.environ,{'XDG_STATE_HOME':directory}):
  transport=CatalogTransport(Client(),{'dataHome':directory,'dataDirs':[],'cacheDir':directory+'/cache'})
  request={'protocolVersion':3,'kind':'motion-preferences-request','binding':Client.bound,'requestId':'7'}
  check('transportReadsActualPrivateStore',transport.handle(request)['snapshot']==committed)
  rejects('wrongBindingRejected',lambda:transport.handle({**request,'binding':{**Client.bound,'frontend':'2'}}))
  check('transportSaveReturnsExactCorrelation',transport.handle({**request,'kind':'motion-preferences-write','requestId':'8','proposal':{**committed,'override':None}})=={'protocolVersion':3,'kind':'motion-preferences-outcome','binding':Client.bound,'requestId':'8','status':'Saved','snapshot':{**committed,'revision':'5','override':None}})
print(json.dumps({'passed':True,'checks':checks,'scope':'Actual private durable store/adapter; original native presentation, keyboard and restart qualification remain separate.'}))

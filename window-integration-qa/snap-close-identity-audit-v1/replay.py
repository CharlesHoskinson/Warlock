"""Sandbox replay of unchanged backend old-close/new-record race. No compositor."""
from pathlib import Path
import hashlib,importlib.machinery,importlib.util,json,os,sys,tempfile
QA=Path('/home/hoskinson/window-integration-qa');sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent

def main():
 scope=require_qa_scope();report=B/'report.json';assert not report.exists()
 source=Path('/home/hoskinson/.local/bin/hypr-snap-groups');digest=hashlib.sha256(source.read_bytes()).hexdigest()
 loader=importlib.machinery.SourceFileLoader('actual_snap_groups',str(source));spec=importlib.util.spec_from_loader(loader.name,loader);m=importlib.util.module_from_spec(spec);loader.exec_module(m)
 # Every source selector/IPC is intercepted before calling actual main.
 def no_ipc(*args):raise AssertionError('Compositor IPC forbidden in offline replay')
 m.ctl=no_ipc;m.compositor_instance=lambda:'offline-owned-sandbox'
 with tempfile.TemporaryDirectory(prefix='snap-close-',dir=B) as path:
  m.ROOT=Path(path);new={'address':'0xbeef','stableId':'new-lifetime','pid':123,'initialClass':'owned-fixture','class':'owned-fixture','mapped':True,'workspace':{'name':'1'},'monitor':0,'at':[100,250],'size':[460,300]}
  m.clients=lambda:[dict(new)]
  state={'version':1,'instance':'offline-owned-sandbox','snapped':{},'groups':[],'next_id':0}
  m.record(state,[new],new['address'],'left',normal_size=[460,300],normal_position=[100,250])
  before=json.loads(json.dumps(state));assert before['snapped']['0xbeef']['identity']==m.identity(new)
  (m.ROOT/'state.json').write_text(json.dumps(state))
  originalArgv=sys.argv
  try:sys.argv=[str(source),'unsnap','0xbeef'];m.main()
  finally:sys.argv=originalArgv
  after=json.loads((m.ROOT/'state.json').read_text())
  observed='0xbeef' not in after['snapped']
  assert observed
 result={'result':'confirmed offline negative counterexample','actualSource':str(source),'actualSourceSHA256':digest,'scope':scope,'noIPC':True,'nativeExecuted':False,'syntheticFixtureIdentityOnly':True,'before':before,'after':after,'oldCloseRequest':['unsnap','0xbeef'],'newRecordRemoved':observed,'boundary':'Executes unchanged helper against sandbox state and synthetic client snapshot; actual address-reuse/native scheduling not exercised'}
 assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
 report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('result','newRecordRemoved','noIPC','nativeExecuted','scope')}))
if __name__=='__main__':main()

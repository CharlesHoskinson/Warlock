"""Protected real selector body with native-object substitutes; no ABI/input acceptance."""
import hashlib,json,pathlib,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
out=root/'qa/runs'/('modal-recipient-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
header=root/'native/core/ModalRecipient.hpp';fixture=root/'qa/check-modal-recipient.cpp'
r={'passed':False,'scope':__doc__,'protectedScope':scope,'nativeAcceptance':False,'inputs':{str(p.relative_to(root)):sha(p) for p in [header,fixture]},'commands':[]}
try:
 shim=out/'shims';shim.mkdir()
 for rel in ['WindowPolicy.hpp','desktop/state/WindowState.hpp','desktop/view/Window.hpp','desktop/Workspace.hpp','protocols/XDGShell.hpp','protocols/XDGDialog.hpp']:
  p=shim/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('// Isolated object substitute declared by the fixture.\n')
 for name,cmd in [('compile',['c++','-std=c++23','-I'+str(root/'native/core'),'-I'+str(shim),str(fixture),'-o',str(out/'test')]),('behavior',[str(out/'test')])]:
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=120);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode})
  if p.returncode:raise RuntimeError(p.stderr or p.stdout)
 assert sha(header)==r['inputs']['native/core/ModalRecipient.hpp'];r['passed']=True
except Exception as error:r['error']=repr(error)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(out/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])

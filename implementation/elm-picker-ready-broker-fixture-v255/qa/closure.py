"""Verify actual frozen backend binding and archive unchanged fixture controls."""
import hashlib,importlib.util,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('current_actual_receipt_wrapper',ROOT/'receipt/qa/wrapper.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
captured=w.verified_backend_root();source=REPO/'implementation/elm-picker-ready-gui-v231'
assert captured==source/'qa/build-1791142801917720234/inputs/adapter'
assert all(p.read_bytes()==(source/'adapter'/p.name).read_bytes() for p in captured.glob('*.py'))
reports=list((ROOT/'receipt/qa').glob('hold-*/report.json'))+list((ROOT/'relay/qa').glob('test-*/report.json'))
assert len(reports)==2 and all(json.loads(p.read_text())['passed'] for p in reports)
receipt=ROOT/'receipt/qa/held-source-manifest.json';r=json.loads(receipt.read_text())
for name,row in r['files'].items():assert sha(ROOT/'receipt'/name)==row['sha256']
spec=importlib.util.spec_from_file_location('current_bound_relay',ROOT/'relay/qa/relay.py');relay=importlib.util.module_from_spec(spec);spec.loader.exec_module(relay)
assert relay.verify_receipt(ROOT/'receipt')==ROOT/'receipt/qa/broker-entrypoint.py'
binding=ROOT/'qa/profile-binding';binding.mkdir(mode=0o700);runtime=binding/'runtime';runtime.mkdir(mode=0o700);control=binding/'control';control.mkdir(mode=0o700)
authority=binding/'authority.json';authority.write_text(json.dumps({'runtime':str(runtime),'instance':'owned_binding'}));authority.chmod(0o600)
receipt_config=binding/'receipt.json';receipt_config.write_text(json.dumps({'authorityConfig':str(authority)}));receipt_config.chmod(0o600)
common={'controlDirectory':str(control),'runtime':str(runtime),'instance':'owned_binding'}
assert relay.command_for(dict(common,profile='broker',authorityConfig=str(authority)),REPO)==['/usr/bin/python3','-B',str(captured/'daemon.py'),str(authority)]
assert relay.command_for(dict(common,profile='receipt',receiptConfig=str(receipt_config)),REPO)==['/usr/bin/python3','-B',str(ROOT/'receipt/qa/broker-entrypoint.py'),str(receipt_config)]
files=[]
for p in sorted(ROOT.rglob('*')):
 if p==ROOT/'component-manifest.json':continue
 st=p.lstat();row={'path':str(p.relative_to(ROOT)),'mode':stat.S_IMODE(st.st_mode)}
 if p.is_symlink():row['symlink']=os.readlink(p)
 elif p.is_file():row.update(sha256=sha(p),size=st.st_size)
 elif p.is_dir():continue
 else:raise RuntimeError('Runtime special file '+str(p))
 files.append(row)
manifest={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'releaseAcceptance':False,'backendRoot':str(captured),'componentSHA256':sha(REPO/'implementation/elm-picker-ready-source-held-v238/source-manifest.json'),'reports':[{'path':str(p),'sha256':sha(p)} for p in reports],'files':files,'scope':'Source/build binding corrected only; unchanged receipt and relay CPU checks, actual captured231 adapter bytes equal current231 source, native reconnect separate'}
with (ROOT/'component-manifest.json').open('x') as f:f.write(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'capturedBackend':str(captured),'files':len(files),'manifestSHA256':sha(ROOT/'component-manifest.json')}))

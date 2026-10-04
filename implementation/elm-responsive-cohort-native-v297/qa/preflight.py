"""Review exact current source, immutable original oracles and owning failure target."""
import ast,hashlib,json,os,resource,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=REPO/'implementation/elm-cohort-native-v183/qa/native.py';source=ROOT/'qa/native.py';a=ast.parse(old.read_text());b=ast.parse(source.read_text())
def calls(t):return [ast.dump(n,include_attributes=False) for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='check']
assert calls(a)==calls(b)
code=source.read_text();assert code.count("signal.pidfd_send_signal(renderer_fd,signal.SIGKILL,None,0)")==2 and "assert start_time(renderer['pid'])==renderer['start']" in code
assert "wait(lambda:s.data('clients')==[])" in code and 'xwayland={enabled=false}' in code
assert 'def wait(fn,seconds=6):' in code and "if time.monotonic()>=until:raise RuntimeError('Unchanged observation deadline')" in code
runtime=REPO/'implementation/elm-picker-ready-runtime-v239';pair=json.loads((runtime/'qa/build-pair-manifest.json').read_text());assert pair['passed']
inputs={}
def check(path,digest):path=Path(path);assert sha(path)==digest,str(path);inputs[str(path)]=digest
for name,digest in pair['files'].items():check(runtime/name,digest)
for row in pair['nativePair'].values():check(row['path'],row['sha256'])
acceptance=REPO/'implementation/elm-keyboardless-current-acceptance-v222/acceptance-manifest.json';check(acceptance,'bbb42789486071600535cf66d4ba869722530c6fe590cc7f1af72a203fc80fe4');held=json.loads(acceptance.read_text());assert held['nativePair']==pair['nativePair'] and held['acceptedGuiNativeCheckCount']==473 and not held['fullReleaseAccepted']
for row in held['files']:
 path=REPO/row['path']
 if 'symlink' in row:assert path.is_symlink() and os.readlink(path)==row['symlink']
 else:check(path,row['sha256'])
gate=REPO/'implementation/elm-picker-ready-source-held-v238/source-manifest.json';check(gate,'078c5f6f090a94f023b0c75b0ed643244860bcf9eceb5388f72884bad79370ff');candidate=json.loads(gate.read_text());assert candidate['sourceHeld'] and candidate['compiled'] and candidate['evidenceIntegrityPassed'] and not candidate['nativeAcceptance']
assert pair['producerEvidence']==str(gate) and pair['producerEvidenceSHA256']==sha(gate)
for row in candidate['files']:
 path=REPO/row['path']
 if 'symlink' in row:assert path.is_symlink() and os.readlink(path)==row['symlink']
 else:check(path,row['sha256'])
gui=REPO/'implementation/elm-responsive-surfaces-gui-v278';build=gui/'qa/build-1791147765154709569/report.json';m=json.loads(build.read_text());assert m['passed'];check(build,sha(build));check(build.parent/'elm-host',m['binarySHA256'])
for rel,digest in m['inputs'].items():check(gui/rel,digest);check(build.parent/'inputs'/rel,digest)
for section in ['compilerDependencies','linkedLibraries']:
 for path,row in m[section].items():check(path,row['sha256'] if isinstance(row,dict) else row)
supervisor=REPO/'implementation/elm-responsive-cohort-v296'
for path in sorted(supervisor.glob('*')):
 if path.is_file():check(path,sha(path))
for path,digest in json.loads((supervisor/'runtime-manifest.json').read_text())['files'].items():check(path,digest)
for path in [source,ROOT/'fixture.py',ROOT/'qa/inspection.py',ROOT/'qa/sampling.py',ROOT/'SPEC.md',ROOT/'lineage.json',Path(__file__),runtime/'qa/build-pair-manifest.json',old]:check(path,sha(path))
current=REPO/'implementation/elm-responsive-regression-held-v294/acceptance-manifest.json';check(current,'bba084a81316cdfeba6840d74af43547b2d73cb81f4cca8004d54fab6a24da69')
assert json.loads(current.read_text())['acceptedCurrentGuiGeneralNativeCheckCount']==473
source_hold=REPO/'implementation/elm-responsive-source-held-v291/source-manifest.json';check(source_hold,'0b1adf3714a570fb66e9ed6e8a2e5f61ef61de3f8ae63ce2923246d666bb4b61');held=json.loads(source_hold.read_text());assert REPO/held['source']==gui
for row in held['files']:
 path=REPO/row['path']
 if 'symlink' in row:assert path.is_symlink() and os.readlink(path)==row['symlink']
 else:check(path,row['sha256'])
for name in ('cohort.py','supervisor.py'):
 prior=REPO/'implementation/elm-picker-ready-cohort-v266'/name;assert prior.read_bytes()==(supervisor/name).read_bytes();check(prior,sha(prior))
r={'passed':True,'nativeAcceptance':False,'scope':'Original183 native recovery UI/cohort oracle and current291/candidate278 source/ABI closure;238/222 ancestry only; stricter unchanged6s completion, PIDFD-owned renderer SIGKILL and empty census before unload; no native result','originalCheckCalls':len(calls(a)),'inputs':inputs}
with (ROOT/'qa/preflight.json').open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':True,'inputs':len(inputs),'originalCheckCalls':len(calls(a))}))

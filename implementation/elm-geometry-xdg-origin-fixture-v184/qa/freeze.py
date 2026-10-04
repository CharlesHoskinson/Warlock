"""Verify exact fixture compilation/CPU evidence and hold immutable inventory."""
import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
build=ROOT/'qa/client-build-1791128443207969331/report.json';b=json.loads(build.read_text());assert b['passed']
test=ROOT/'qa/test-1791128474911399590/report.json';t=json.loads(test.read_text());assert t['passed'] and t['buildReportSHA256']==sha(build)
assert t['runs']['actual']['helperChecks']==50 and t['runs']['actual']['failures']==0 and t['runs']['actual']['connections']==0 and len(t['cli'])==25
assert len(t['runs'])==4 and all(row['failures']>0 and row['exitCode']==1 and row['connections']==0 for name,row in t['runs'].items() if name!='actual')
assert sha(ROOT/'native/xdg-origin-client.c')==t['runs']['actual']['sourceSHA256']
external={}
for section in ['inputs','dependencies','tools','linkedLibraries']:
 for path,d in b[section].items():
  p=Path(path);assert sha(p)==d,path
  if not p.is_relative_to(ROOT):external[path]={'sha256':d,'size':p.stat().st_size,'resolved':str(p.resolve())}
assert sha(b['client'])==b['clientSHA256']
for path,d in t['sourceInputs'].items():assert sha(path)==d,path
for report in ROOT.glob('qa/*/report.json'):
 data=json.loads(report.read_text())
 for rel,d in data.get('artifacts',{}).items():assert sha(report.parent/rel)==d,(report,rel)
for path in [REPO/'implementation/elm-window-geometry-v16/core/qa/xdg-max-client.c',REPO/'implementation/elm-window-geometry-v16/core/qa/build-client.py',REPO/'implementation/elm-geometry-nonzero-origin-source-contract-v175/component-manifest.json']:
 external[str(path)]={'sha256':sha(path),'size':path.stat().st_size}
desc=ROOT/'client-build-report.json';assert not desc.exists()
desc.write_text(json.dumps({'scope':'Controlled XDG fixture CPU compile/tests only; no native/GTK acceptance','client':{'path':b['client'],'sha256':b['clientSHA256'],'buildReport':str(build),'buildReportSHA256':sha(build)},'cpuReport':str(test),'cpuReportSHA256':sha(test),'nativeAcceptance':False},indent=2)+'\n')
target=ROOT/'component-manifest.json';assert not target.exists()
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':p.stat().st_mode&0o7777} for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=target}
manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Actual controlled XDG fixture compile and CPU characterization; not native rendering/input or GTK qualification','nativeAcceptance':False,'modelAcceptance':False,'policyAcceptance':False,'files':files,'externalClosure':external,'buildReport':str(build),'buildReportSHA256':sha(build),'testReport':str(test),'testReportSHA256':sha(test),'helperChecks':50,'cliCases':25,'unsafeCompiledControlsRejected':3,'sourceSHA256':sha(ROOT/'native/xdg-origin-client.c')}
target.write_text(json.dumps(manifest,indent=2)+'\n')
for rel,row in files.items():assert sha(ROOT/rel)==row['sha256'],rel
print(json.dumps({'passed':True,'files':len(files),'dependencies':len(b['dependencies']),'tools':len(b['tools']),'libraries':len(b['linkedLibraries']),'manifest':str(target),'manifestSHA256':sha(target),'client':b['client'],'clientSHA256':b['clientSHA256']}))

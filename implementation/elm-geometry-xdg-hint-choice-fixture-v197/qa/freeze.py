"""Hold exact protocol-informed client choice and CPU evidence; never GUI."""
import ast,hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OLD=REPO/'implementation/elm-geometry-xdg-origin-fixture-v184'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
build=ROOT/'qa/client-build-1791129756017735997/report.json';b=json.loads(build.read_text());assert b['passed']
test=ROOT/'qa/test-1791129836690118791/report.json';t=json.loads(test.read_text());assert t['passed'] and t['buildReportSHA256']==sha(build)
assert t['runs']['actual']['helperChecks']==75 and t['runs']['actual']['failures']==0 and t['runs']['actual']['connections']==0 and len(t['cli'])==25
assert t['callback']['callbackChecks']==7 and t['callback']['failures']==0
assert len(t['runs'])==6 and all(row['failures']>0 and row['exitCode']==1 and row['connections']==0 for name,row in t['runs'].items() if name!='actual')
assert sha(ROOT/'native/xdg-origin-client.c')==t['runs']['actual']['sourceSHA256']
helper=(ROOT/'qa/helper-test.c').read_text();start=helper.index('    int cw,ch;struct profile choice=');end=helper.index('    printf("{\\"helperChecks',start)
assert (helper[:start]+helper[end:]).encode()==(ROOT/'qa/original-helper-test.c').read_bytes()==(OLD/'qa/helper-test.c').read_bytes()
def cases(path):
 tree=ast.parse(path.read_text());return [ast.dump(n.value) for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='cases' for x in n.targets)]
assert cases(ROOT/'qa/test-final.py')==cases(OLD/'qa/test-current.py')
assert (ROOT/'qa/build.py').read_bytes()==(OLD/'qa/build.py').read_bytes()
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
oldmanifest=OLD/'component-manifest.json';m=json.loads(oldmanifest.read_text());assert m['sourceHeld'] and m['evidenceIntegrityPassed']
for rel,row in m['files'].items():assert sha(OLD/rel)==row['sha256'],rel
failure=REPO/'implementation/elm-geometry-xdg-origin-native-v190/qa/native-1791129297579795954/report.json';assert not json.loads(failure.read_text())['passed']
for path in [oldmanifest,failure,OLD/'native/xdg-origin-client.c',OLD/'qa/helper-test.c',OLD/'qa/test-current.py']:
 external[str(path)]={'sha256':sha(path),'size':path.stat().st_size}
desc=ROOT/'client-build-report.json';assert not desc.exists()
desc.write_text(json.dumps({'scope':'Controlled XDG hint-choice fixture CPU compile/tests only; no native/GTK acceptance','client':{'path':b['client'],'sha256':b['clientSHA256'],'buildReport':str(build),'buildReportSHA256':sha(build)},'cpuReport':str(test),'cpuReportSHA256':sha(test),'nativeAcceptance':False},indent=2)+'\n')
target=ROOT/'component-manifest.json';assert not target.exists()
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':p.stat().st_mode&0o7777} for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=target}
packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Actual protocol-informed ordinary client choice compile/CPU; state-specific mandatory MAX remains exact, no native/GTK/model/policy acceptance','nativeAcceptance':False,'modelAcceptance':False,'policyAcceptance':False,'files':files,'externalClosure':external,'buildReport':str(build),'buildReportSHA256':sha(build),'testReport':str(test),'testReportSHA256':sha(test),'helperChecks':75,'originalHelperChecksBytePreserved':50,'newChoiceChecks':25,'callbackChecks':7,'cliCasesBytePreserved':25,'unsafeCompiledControlsRejected':5,'sourceSHA256':sha(ROOT/'native/xdg-origin-client.c'),'ancestorManifest':str(oldmanifest),'ancestorManifestSHA256':sha(oldmanifest),'preservedNativeFailure':str(failure),'preservedNativeFailureSHA256':sha(failure)}
target.write_text(json.dumps(packet,indent=2)+'\n')
for rel,row in files.items():assert sha(ROOT/rel)==row['sha256'],rel
print(json.dumps({'passed':True,'files':len(files),'dependencies':len(b['dependencies']),'tools':len(b['tools']),'libraries':len(b['linkedLibraries']),'manifest':str(target),'manifestSHA256':sha(target),'client':b['client'],'clientSHA256':b['clientSHA256']}))

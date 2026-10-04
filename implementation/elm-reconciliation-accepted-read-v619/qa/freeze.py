import hashlib,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def latest(pattern):return max((ROOT/'qa').glob(pattern),key=lambda p:p.parent.name)
primary=latest('tests-*/report.json');mutants=latest('mutations-*/report.json');build=latest('build-*/report.json');model=latest('model-*/report.json')
p=json.loads(primary.read_text());m=json.loads(mutants.read_text());b=json.loads(build.read_text());q=json.loads(model.read_text())
assert p['passed'] and len(p['checks'])==51 and m['passed'] and len(m['controls'])==13 and b['passed'] and q['passed'] and q['named']==9 and q['mutants']==4
assert q['sourceSHA256']==sha(ROOT/'spec/accepted.qnt')
for source in (ROOT/'src').glob('*.elm'):
 assert sha(source)==sha(primary.parent/'inputs/src'/source.name)==sha(build.parent/'inputs/src'/source.name)
 if source.name!='ReconciliationTracking.elm':assert sha(source)==sha(ROOT.parent/'elm-reconciliation-frontend-v611/src'/source.name)
assert m['primaryReport']==str(primary)
versions=[]
for command in [['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','--version'],['node','--version'],['quint','--version']]:
 result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=90);assert result.returncode==0;versions.append({'command':command,'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
(ROOT/'qa/versions.json').write_text(json.dumps(versions,indent=2)+'\n')
files={str(path.relative_to(ROOT)):sha(path) for path in sorted(ROOT.rglob('*')) if path.is_file() and path.name!='component-manifest.json'}
manifest={'schema':1,'component':ROOT.name,'sourceHeld':True,'frozenAtUnixNs':time.time_ns(),'nativeAcceptance':False,'productionWired':False,'releaseDeliveryLossAcceptance':False,'acceptedReadDrainCPUAcceptance':True,'primaryReport':str(primary.relative_to(ROOT)),'checks':51,'mutationReport':str(mutants.relative_to(ROOT)),'compiledMutations':13,'buildReport':str(build.relative_to(ROOT)),'modelReport':str(model.relative_to(ROOT)),'namedModelCases':9,'sampledTraces':500,'maxModelSteps':25,'typedModelMutants':4,'files':files}
(ROOT/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'frozen':True,'files':len(files),'manifest':str(ROOT/'component-manifest.json')}))

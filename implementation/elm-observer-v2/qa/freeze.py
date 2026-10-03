"""Bind reviewed current observer inputs to applied CPU, Quint and mutation receipts."""
import datetime,hashlib,json,resource
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def latest(pattern):
 files=sorted((ROOT/'qa').glob(pattern))
 assert files,pattern
 return files[-1]
def verify(path):
 report=json.loads(path.read_text());assert report['passed'],path
 for relative,digest in report['artifacts'].items():assert sha(path.parent/relative)==digest,(path,relative)
 return report
run=latest('run-*/report.json');report=verify(run)
for relative,digest in report['inputs'].items():assert sha(ROOT/relative)==digest,relative
mutations=latest('mutations-*/report.json');mutation=verify(mutations)
assert mutation['sourceSHA256']==sha(ROOT/'src/Observer.elm')
for row in mutation['mutations']:
 assert row['mutationDetected'] and row['actualFailedChecks'],row
 directory=mutations.parent/row['name']
 for p in (ROOT/'src').glob('*.elm'):
  if p.name!='Observer.elm':assert sha(directory/'src'/p.name)==sha(p),p
 assert sha(directory/'check.cjs')==sha(ROOT/'qa/check.cjs')
elm=json.loads((run.parent/'elm-report.json').read_text())
conformance=json.loads((run.parent/'conformance-report.json').read_text())
manifest={'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'scope':'Pure Elm observation policy CPU/protocol evidence only; native integration and all release cycles remain incomplete','runReport':str(run.relative_to(ROOT)),'mutationReport':str(mutations.relative_to(ROOT)),'checks':{'elmReplayCases':elm['testCount'],'counterSuccessors':elm['counterSuccessorChecks'],'counterComparisons':elm['counterComparisonChecks'],'quintNamedTests':12,'quintInvariantSamples':1000,'quintMaxSteps':40,'actualITFReplayTraces':conformance['traceCount'],'actualITFReplayTransitions':conformance['stepCount'],'compiledUnsafeMutantsDetected':len(mutation['mutations'])},'requirementsInProgress':['ELM-ARC-010','ELM-REV-008'],'completedRequirements':[]}
manifest['files']={str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='slice-manifest.json'}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2))

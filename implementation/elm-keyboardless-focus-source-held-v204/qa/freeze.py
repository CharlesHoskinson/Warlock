"""Source/model/actual-method/full-TU gate; no native acceptance asserted."""
import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
model=REPO/'implementation/elm-keyboardless-focus-model-v201/qa/model-1791138368784199775/report.json';m=json.loads(model.read_text());assert m['passed'] and len(m['namedScenarios'])==17 and m['mutantsRejected']==9 and m['invariantSamples']==1000
compile=REPO/'implementation/elm-keyboardless-focus-compile-v202/compile-1791138502101316887/report.json';c=json.loads(compile.read_text());assert c['passed'] and len(c['owningHeaders'])==694 and sha(c['object'])==c['objectSHA256'] and sha(c['source'])==c['sourceSHA256']
for path,digest in c['dependencies'].items():assert sha(path)==digest
methods=REPO/'implementation/elm-keyboardless-method-controls-v203/qa/methods-1791138899560511298/report.json';a=json.loads(methods.read_text());assert a['passed'] and len(a['controls'])==8 and a['sourceSHA256']==c['sourceSHA256']
for row in a['controls']:assert row['accepted'] and row['exitCode']==(0 if row['name']=='baseline' else 1)
assert (methods.parent/'baseline.stdout').read_text().strip()=='actual-seat-method-checks: 22'
for p,report in [(model,m),(compile,c),(methods,a)]:
 for rel,digest in report['artifacts'].items():assert sha(p.parent/rel)==digest
assert not json.loads((REPO/'implementation/elm-keyboardless-focus-model-v199/qa/model-1791138318506994994/report.json').read_text())['passed']
files=[]
names=['elm-keyboardless-popup-focus-v196','elm-keyboardless-focus-model-v199','elm-keyboardless-focus-source-v200','elm-keyboardless-focus-model-v201','elm-keyboardless-focus-compile-v202','elm-keyboardless-method-controls-v203','elm-keyboardless-focus-source-held-v204']
for name in names:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  if p==ROOT/'qa/slice-manifest.json':continue
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if p.is_symlink():row['target']=os.readlink(p)
  elif p.is_file():row.update(sha256=sha(p),size=st.st_size)
  elif p.is_dir():continue
  else:raise RuntimeError('Unexpected special file '+str(p))
  files.append(row)
assert len(files)>700
result={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'releaseAcceptance':False,'modelNamed':17,'modelTraces':1000,'modelControls':9,'actualMethodChecks':22,'actualMethodControls':7,'reports':[str(p) for p in [model,compile,methods]],'files':files,'scope':'Exact SeatManager source/model/actual extracted methods and owning full-TU compilation; source/header/code/refinement gates only, no native correction or full release'}
with (ROOT/'qa/slice-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'manifestSHA256':sha(ROOT/'qa/slice-manifest.json')}))

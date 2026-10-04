import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=REPO/'implementation/elm-picker-ready-gui-v231';old=REPO/'implementation/elm-stable-surface-publication-v521'
changed=[]
for directory in ['src','native','adapter','assets']:
 a={str(p.relative_to(old)) for p in (old/directory).rglob('*') if p.is_file()};b={str(p.relative_to(source)) for p in (source/directory).rglob('*') if p.is_file()};assert a==b
 for relative in sorted(a):
  if sha(old/relative)!=sha(source/relative):changed.append(relative)
assert changed==['src/Desktop.elm'] and sha(source/'elm.json')==sha(old/'elm.json')
reports=[]
for rootname,pattern in [('elm-picker-captured-controller-v228','replay-*/report.json'),('elm-picker-readiness-model-v230','model-*/report.json'),('elm-picker-ready-gui-v231','build-*/report.json'),('elm-picker-controller-refinement-v237','refine-*/report.json')]:
 candidates=list((REPO/'implementation'/rootname/'qa').glob(pattern));assert len(candidates)==1;p=candidates[0];m=json.loads(p.read_text());assert m['passed']
 for relative,digest in m.get('artifacts',{}).items():assert sha(p.parent/relative)==digest,relative
 for relative,digest in m.get('inputs',{}).items():
  actual=Path(relative) if Path(relative).is_absolute() else source/relative
  assert sha(actual)==digest,relative
 for section in ['compilerDependencies','linkedLibraries','tools']:
  for path,row in m.get(section,{}).items():assert sha(path)==(row['sha256'] if isinstance(row,dict) else row)
 reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':True})
 if rootname.endswith('v230'):assert len(m['namedScenarios'])==22 and m['invariantSamples']==1000 and m['maxSteps']==40 and m['mutantsRejected']==13
 if rootname.endswith('v237'):assert m['cases']==27 and m['compiledControlsRejected']==8 and all(c['compiled'] and c['normalExitCode']==0 and c['rejected'] for c in m['controls'])
files=[]
roots=['elm-picker-captured-controller-v228','elm-picker-readiness-model-v229','elm-picker-readiness-model-v230','elm-picker-ready-gui-v231']+['elm-picker-controller-refinement-v'+str(n) for n in range(232,238)]+[ROOT.name]
for name in roots:
 for path in sorted((REPO/'implementation'/name).rglob('*')):
  if path==ROOT/'source-manifest.json':continue
  st=path.lstat();row={'path':str(path.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if path.is_symlink():row['symlink']=os.readlink(path)
  elif path.is_file():row.update(sha256=sha(path),size=st.st_size)
  elif path.is_dir():continue
  else:raise RuntimeError('Unexpected special file '+str(path))
  files.append(row)
result={'passed':True,'sourceHeld':True,'compiled':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullRoadmapAccepted':False,'fullReleaseAccepted':False,'source':str(source.relative_to(REPO)),'changedSourceFiles':changed,'reports':reports,'files':files,'scope':'Model-qualified actual compiled choice/return-focus paired observation readiness; includes all failed CPU fixture attempts; prospective native qualification only'}
with (ROOT/'source-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'manifestSHA256':sha(ROOT/'source-manifest.json')}))

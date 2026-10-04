import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=REPO/'implementation/elm-current-renderer-preflight-bound-v225/qa/native-1791141533677873665/report.json';m=json.loads(p.read_text());assert not m['passed'] and m['cleanupPassed'] and not m['inputChanges'] and len(m['checks'])==5 and m['error']=="RuntimeError('Unchanged observation deadline')" and 'faultInjection' not in m
for rel,digest in m['artifacts'].items():assert sha(p.parent/rel)==digest
for path,digest in m['inputs'].items():assert sha(path)==digest
witness=REPO/'implementation/elm-picker-joint-observation-v226/witness.json';w=json.loads(witness.read_text());assert sha(w['nativeReport'])==w['nativeReportSHA256'] and sha(w['nativeLog'])==w['nativeLogSHA256'] and sha(w['source'])==w['sourceSHA256'] and sha(w['shell'])==w['shellSHA256'];assert not w['rendererFaultReached'] and not w['effectRequests']
files=[]
for name in ['elm-current-renderer-recovery-v224','elm-current-renderer-preflight-bound-v225','elm-picker-joint-observation-v226','elm-picker-failure-source-held-v227']:
 for path in sorted((REPO/'implementation'/name).rglob('*')):
  if path==ROOT/'failure-manifest.json':continue
  st=path.lstat();row={'path':str(path.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if path.is_symlink():row['symlink']=os.readlink(path)
  elif path.is_file():row.update(sha256=sha(path),size=st.st_size)
  elif path.is_dir():continue
  else:raise RuntimeError('Unexpected special file '+str(path))
  files.append(row)
result={'sourceHeld':True,'evidenceIntegrityPassed':True,'passed':True,'nativeAcceptance':False,'rendererFaultReached':False,'pickerActivationAccepted':False,'fullRoadmapAccepted':False,'fullReleaseAccepted':False,'reports':[{'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':False,'checksReached':5,'cleanupPassed':True}], 'witness':str(witness.relative_to(REPO)),'witnessSHA256':sha(witness),'files':files,'scope':'Preserved actual current225 picker activation timeout before renderer fault; closure and normal teardown only, exact native/order hypothesis awaiting controller replay and model-qualified repair'}
with (ROOT/'failure-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'manifestSHA256':sha(ROOT/'failure-manifest.json')}))

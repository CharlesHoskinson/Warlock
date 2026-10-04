import copy,hashlib,json,re,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
paths=[REPO/'implementation/elm-native-owner-turn-interleave-before-run-v557/qa/native-1791141409239925060/report.json',REPO/'implementation/elm-native-owner-turn-interleave-current-run-v558/qa/native-1791141432343331863/report.json']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify(path,old):
 j=json.loads(path.read_text());assert j['cleanupPassed'] and not j['mainDesktopActions'];assert j['passed']==(not old);assert all(c['passed'] for c in j['checks'])
 if old:assert j['error']=="RuntimeError('Unchanged observation deadline')" and len(j['checks'])==4
 else:assert len(j['checks'])==89
 for rel,digest in j['artifacts'].items():assert sha(path.parent/rel)==digest
 log=path.parent/'native-evidence/elm-webview.log';lines=log.read_text().splitlines();holds=[(i,re.fullmatch(r'qa-interleave-hold: publication=(\d+) proof=(\d+)',x)) for i,x in enumerate(lines) if x.startswith('qa-interleave-hold:')];resumes=[(i,re.fullmatch(r'qa-interleave-resume: publication=(\d+) proof=(\d+) age=(\d+)',x)) for i,x in enumerate(lines) if x.startswith('qa-interleave-resume:')];assert len(holds)==len(resumes)==1 and holds[0][1] and resumes[0][1]
 hi,hm=holds[0];ri,rm=resumes[0];hp,proof=map(int,hm.groups());rp,proof2,age=map(int,rm.groups());assert hi<ri and hp==proof==proof2 and 0<=age<=500000
 def commits(start,stop):
  values=[]
  for index in range(start,stop):
   line=lines[index]
   if line.startswith('qa-bridge-input: ') and ' json=' in line:
    value=json.loads(line.split(' json=',1)[1])
    if value.get('kind')=='view-commit':values.append((index,value))
  return values
 previous=commits(0,hi)[-1][1];between=commits(hi+1,ri)
 assert int(previous['projection']['frame']['publication'])==hp
 if old:
  assert rp==hp+1 and len(between)==1
  after=between[0][1];assert after['requests']==after['focus']==[]
  beforeframe=copy.deepcopy(previous['projection']['frame']);afterframe=copy.deepcopy(after['projection']['frame']);beforeframe.pop('publication');afterframe.pop('publication');assert beforeframe==afterframe
  assert any(line=='surface-context-refused: origin-or-proof' for line in lines[ri+1:]);assert not any(line.startswith('surface-context-admitted:') for line in lines)
 else:
  assert rp==hp and not between
  assert any(line.startswith('surface-context-admitted: view=1 generation=1 origin=bar trigger=pointer') for line in lines[ri+1:])
  assert any(line.startswith('qa-pointer-proof: type=7 button=3 ') and ' publication='+str(proof)+' ' in line and ' available=1 ' in line for line in lines[:hi])
 return {'nativeReport':str(path),'nativeReportSHA256':sha(path),'logSHA256':sha(log),'oldController':old,'nativeChecks':len(j['checks']),'publicationBefore':hp,'publicationAfter':rp,'proofPublication':proof,'proofAgeMicroseconds':age,'interveningCommits':len(between),'fullFrameIdenticalExcludingPublication':True,'cleanupPassed':True,'artificialScheduling':True}
results=[verify(p,i==0) for i,p in enumerate(paths)]
assert json.loads(paths[0].read_text())['pair']==json.loads(paths[1].read_text())['pair']
report={'passed':True,'nativeAcceptance':True,'scope':'Controlled actual physical input/native owner-update publication/real async DOM counterfactual on owning470tuple; diagnostic QA derivatives only','checks':results,'controlledMechanismConfirmed':True,'historical504CauseConfirmed':False,'pointerRaceCausallyResolved':False,'fullReleaseAccepted':False,'completedRequirementIds':[]}
p=ROOT/'qa/report.json';assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(p),'ages':[r['proofAgeMicroseconds'] for r in results]}))

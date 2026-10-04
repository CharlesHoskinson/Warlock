import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=REPO/'implementation/elm-xdg-origin-menu-regression-v478/qa/native-1791134835598728098/report.json';j=json.loads(p.read_text());log=p.parent/'native-evidence/elm-webview.log';lines=log.read_text().splitlines();requests=[json.loads(l.split(': ',1)[1]) for l in lines if l.startswith('frontend-request: ')];frames=[json.loads(l.split(': ',1)[1]) for l in lines if l.startswith('backend-frame: ')];inspections=[json.loads(l.split(': ',1)[1]) for l in lines if l.startswith('surface-inspection: ')]
request=next(r for r in requests if r.get('kind')=='projection-request' and r.get('requestId')=='58');assert not any(f.get('kind')=='action-projection' and f.get('requestId')=='58' for f in frames)
geometry=next(f for f in frames if f.get('kind')=='geometry-facts' and f.get('requestId')=='59');assert geometry['binding']==request['binding'] and geometry['facts']['windows'];assert inspections[-1]['body']['phase']=='Awaiting' and inspections[-1]['body']['groups']==[] and inspections[-1]['body']['outstanding']==0
assert j['cleanupPassed'] and not j['passed'] and len(j['checks'])==86 and j['error']=="RuntimeError('Unchanged observation deadline')"
daemon=REPO/'implementation/elm-shared-geometry-carrier-v422/adapter/daemon.py';shell=REPO/'implementation/elm-shared-geometry-carrier-v422/src/Shell.elm';assert "if scene is None:send({'protocolVersion':3,'kind':'host-refresh'})" in daemon.read_text();assert 'model.expected/=Nothing' in shell.read_text()
out=ROOT/'qa'/('diagnosis-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps({'passed':True,'scope':'Actual failed478 log/source terminal-read liveness diagnosis; no handler/model or native repair qualification','unansweredProjection':request,'latestGeometry':geometry,'finalInspection':inspections[-1],'inputs':{str(q):sha(q) for q in [Path(__file__),p,log,daemon,shell]},'causalNativeFixAccepted':False},indent=2)+'\n');print(json.dumps({'passed':True,'unansweredProjection':'58','geometryReply':'59','report':str(out/'report.json')}))

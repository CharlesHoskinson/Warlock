import hashlib,json,re,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=REPO/'implementation/elm-pending-observation-recovery-trace-v573/qa/native-1791143276230101221/report.json';j=json.loads(p.read_text());assert not j['passed'] and j['cleanupPassed'] and len(j['checks'])==75 and all(c['passed'] for c in j['checks']);assert j['error']=="RuntimeError('Unchanged observation deadline')" and 'click(recovered);recovered_min=wait' in j['traceback'] and not j['mainDesktopActions']
for name,digest in j['artifacts'].items():assert sha(p.parent/name)==digest
log=p.parent/'native-evidence/elm-webview.log';lines=log.read_text().splitlines();events=[];commits=[];backend=[]
for index,line in enumerate(lines):
 if line.startswith('backend-frame: '):backend.append((index,json.loads(line.split(': ',1)[1])))
 if line.startswith('qa-bridge-input: '):
  value=json.loads(line.split(' json=',1)[1]);events.append((index,value))
  if value['kind']=='view-commit':commits.append((index,value))
attached=[(i,v) for i,v in backend if v['kind']=='attached'];assert len(attached)==2;old=attached[0][1]['binding'];new=attached[1][1]['binding'];assert old['lifetime']==new['lifetime'] and old['session']!=new['session']
uncertain=[(i,v) for i,v in backend if v['kind']=='host-uncertain'];assert len(uncertain)==1 and uncertain[0][1]['binding']==new;intent=uncertain[0][1]['intent'];assert intent['operation']=='minimize' and intent['incarnation']=='2' and intent['request']=='12'
i,action=[(i,v) for i,v in events if i>attached[-1][0] and v['kind']=='surface-action' and v['id'].startswith('bar:group:')][-1]
assert lines[i+1].startswith('qa-action-admission: allowed=1 popup=0 view=1 generation=1 ')
previous=[(ci,c) for ci,c in commits if ci<i][-1][1]['projection']['frame'];assert action['publication']==previous['publication'] and action['lease']==previous['lease'];assert any(c['id']==action['id'] and c['enabled'] for c in previous['bar'])
ci,after=[(ci,c) for ci,c in commits if ci>i][0];assert after['requests']==after['focus']==[];assert 'awaits reconciliation' in after['projection']['frame']['status'];assert 'last request could not be confirmed' in after['projection']['frame']['status']
assert not any(line.startswith('frontend-request: ') and json.loads(line.split(': ',1)[1])['kind']=='window-effect' for line in lines[i+1:])
reads=[v for bi,v in backend if attached[-1][0]<bi<i and v['kind'] in ['action-projection','geometry-facts']];assert [v['kind'] for v in reads]==['action-projection','geometry-facts'] and all(v['binding']==new for v in reads)
report={'passed':True,'nativeAcceptance':False,'scope':'Native573 actual current matching enabled click is admitted; Elm rejects retained Unknown reservation despite fresh binding and typed reads. No reconciliation repair acceptance','nativeReport':str(p),'nativeReportSHA256':sha(p),'logSHA256':sha(log),'checksReached':75,'cleanupPassed':True,'nativeActionAdmitted':True,'action':action,'oldBinding':old,'newBinding':new,'unknownIntent':intent,'freshObservationRequestIds':[v['requestId'] for v in reads],'nativeEffectsAfterAction':0,'refusalStatus':after['projection']['frame']['status'],'historicalOutcome':'Unknown','fullReleaseAccepted':False,'completedRequirementIds':[]};out=ROOT/'qa/report.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(out),'nativeActionAdmitted':True}))

import copy,hashlib,json,resource,sys,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];o=r.parent/'elm-gtk-privileged-helper-drain-v282';n=o/'qa/native-1791149554426845000';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(o/'component-manifest.json')=='5619425ec3a4b2d60fb26072d7fd5fbef44e6b2fefda90b3419e4bf37c392233'
hold=json.loads((o/'component-manifest.json').read_text());sourceRows=0
for name,row in hold['files'].items():
 p=o/name;assert sha(p)==row['sha256'] and p.stat().st_size==row['size'];sourceRows+=1
m=json.loads((n/'report.json').read_text());assert m['passed'] and m['cleanupPassed'] and len(m['checks'])==27 and all(x['passed'] for x in m['checks']) and m['fullCampaignPassed'] is False and m['nativeAcceptance'] is False
artifacts=0
for name,h in m['artifacts'].items():assert sha(n/name)==h,name;artifacts+=1
for name,h in m['inputs'].items():
 if isinstance(h,str):assert sha(Path(name))==h,name
post=json.loads((n/'native-evidence/activation-post-retirement.json').read_text());assert post['passed'] and len(post['records'])==9
sys.path.insert(0,str(o/'qa'));from private_bus import Activations;from outcomes import classify
inventory=json.loads((n/'native-evidence/activation-inventory.json').read_text());manager=object.__new__(Activations);manager.records=copy.deepcopy(inventory['services'])
for record in manager.records:record['journalDirectory']=str(n/'native-evidence/activation-journals'/record['name']);record['descriptorCapture']=str(n/'native-evidence/activation-descriptors'/Path(record['descriptorCapture']).name)
snapshots=manager.snapshots();assert len(snapshots)==9;classifications=[]
for record,path,rows in snapshots:
 result=classify(record,rows);classifications.append({'service':record['name'],'journal':str(path),'classification':result})
 terminal=rows[-1];assert terminal['kind']=='terminal' and terminal['error'] is None and not terminal['liveDescendants'] and not terminal['fallback']
 owned={(x['identity']['pid'],x['identity']['start']) for x in rows if x['kind']=='owned-child'};exits={(x['identity']['pid'],x['identity']['start']) for x in rows if x['kind']=='child-exit'};assert owned==exits
 shutdown=next((x for x in rows if x['kind']=='shutdown-request'),None)
 if shutdown:assert terminal['monotonic']-shutdown['monotonic']<2.5
 if record['name']=='org.freedesktop.portal.Documents':
  helper=next(x['identity'] for x in rows if x['kind']=='owned-child' and x['identity']['privilegedCredentials']);assert helper['pid']==3761255 and helper['start']=='11766188'
  assert not any(x['kind']=='signal' and x['identity']['pid']==helper['pid'] for x in rows)
  refusal=next(x for x in rows if x['kind']=='signal-identity-refused');assert refusal['metadata']['exe'] is None and refusal['metadata']['exeError'] and '(fusermount3)' in refusal['metadata']['stat']
  exit=next(x for x in rows if x['kind']=='child-exit' and x['identity']['pid']==helper['pid']);assert exit['waitStatus']==exit['exitCode']==0
  assert exit['observedIdentity']['ppid']==rows[0]['identity']['pid'] and terminal['childExitCode']==0 and len(terminal['allWaitStatuses'])==2
h=m['cleanup'];assert h['runtimeGone'] and not h['remainingDescendants'] and h['privateActivationCleanupPassed'] and h['privateActivationPostRetirement']['passed']
inputs={str(n/'report.json'):sha(n/'report.json'),str(o/'component-manifest.json'):sha(o/'component-manifest.json'),str(o/'qa/private_bus.py'):sha(o/'qa/private_bus.py'),str(o/'qa/outcomes.py'):sha(o/'qa/outcomes.py')}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();report={'passed':True,'diagnosticCleanupQualified':True,'nativeAcceptance':False,'fullCampaignPassed':False,'verifiedSourceRows':sourceRows,'verifiedArtifacts':artifacts,'actualChecks':27,'activationJournals':classifications,'inputs':inputs};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name!='component-manifest.json'};(r/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Actual282 historical tuple27 diagnostic checks and cleanup proof only','files':files,'externalFiles':inputs,'verificationReport':str((out/'report.json').relative_to(r))},indent=2)+'\n');print(json.dumps({'verifiedArtifacts':artifacts,'sourceRows':sourceRows,'manifestSHA256':sha(r/'component-manifest.json')}))

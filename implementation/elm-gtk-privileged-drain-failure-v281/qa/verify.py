import hashlib,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];o=r.parent/'elm-gtk-activation-credentials-fix-v276';n=o/'qa/native-1791148359641279769';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((n/'report.json').read_text());assert not m['passed'] and not m['cleanupPassed'] and len(m['checks'])==27 and all(x['passed'] for x in m['checks'])
count=0
for name,expected in m['artifacts'].items():
 p=n/name;assert p.is_file() and sha(p)==expected,str(p);count+=1
p=next((n/'native-evidence/activation-journals/org.freedesktop.portal.Documents').glob('*.jsonl'));rows=[json.loads(x) for x in p.read_text().splitlines()];priv=next(x['identity'] for x in rows if x['kind']=='owned-child' and x['identity']['privilegedCredentials']);assert priv['pid']==3672157 and priv['start']=='11646706' and priv['realUid']==1000 and priv['effectiveUid']==priv['savedUid']==priv['filesystemUid']==0
assert rows[-1]['kind']=='signal-identity-refused' and rows[-1]['identity']['pid']==priv['pid'] and not any(x['kind']=='terminal' for x in rows)
assert any(x['kind']=='supervisor-failure' and 'cannot be signalled' in x['error'] for x in rows)
log=(n/'native-evidence/privateBus.log').read_text();assert log.count('RuntimeError: privileged or replaced child cannot be signalled')==2
h=m['cleanup'];assert h['privateActivationCleanupPassed'] is False and h['privateActivationPostRetirementError']=="Refused('complete retired activation wrapper')" and h['runtimeGone'] and not h['remainingDescendants']
summary=[]
for q in sorted((n/'native-evidence/activation-journals').glob('*/*.jsonl')):
 v=[json.loads(x) for x in q.read_text().splitlines()];summary.append({'service':q.parent.name,'lastKind':v[-1]['kind'],'childExit':v[-1].get('childExitCode'),'error':v[-1].get('error')})
inputs={str(n/'report.json'):sha(n/'report.json'),str(o/'qa/activation-supervisor.py'):sha(o/'qa/activation-supervisor.py'),str(o/'qa/credentials.py'):sha(o/'qa/credentials.py'),str(p):sha(p),str(n/'native-evidence/privateBus.log'):sha(n/'native-evidence/privateBus.log')}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();report={'passed':True,'actualNativePassed':False,'nativeAcceptance':False,'verifiedArtifacts':count,'recordedPassedChecks':27,'privilegedOwnedChild':priv,'terminalMissing':True,'activationJournals':summary,'inputs':inputs};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
(r/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Actual276 failed native activation drain evidence only','files':files,'externalFiles':inputs,'verificationReport':str((out/'report.json').relative_to(r))},indent=2)+'\n');print(json.dumps({'verifiedArtifacts':count,'manifestSHA256':sha(r/'component-manifest.json')}))

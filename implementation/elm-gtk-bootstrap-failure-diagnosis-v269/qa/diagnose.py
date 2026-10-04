import hashlib,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1]
o=r.parent/'elm-gtk-post-bus-retirement-v263'
n=o/'qa/native-1791145436509122699'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((n/'report.json').read_text());h=json.loads((n/'native-evidence/host-evidence.json').read_text())
ipc=n/'native-evidence/bounded-ipc/1791145441942266662';c=json.loads((ipc/'record.json').read_text());stdout=(ipc/'stdout').read_text()
assert not m['passed'] and m['cleanupPassed'] and len(m['checks'])==9 and all(x['passed'] for x in m['checks'])
assert c['exitCode']==7 and c['argv'][-3:]==['dispatch','setfloating','address:0x55e187200fd0'] and "')' expected near 'address'" in stdout
assert h['privateActivationCleanupPassed'] is False and h['privateActivationPostRetirementError'] and not h['remainingDescendants'] and h['runtimeGone']
p=next((n/'native-evidence/activation-journals/org.freedesktop.portal.Documents').glob('*.jsonl'));rows=[json.loads(x) for x in p.read_text().splitlines()]
assert rows[-1]['error']=="RuntimeError('missing unique PID/start before reap')" and rows[-1]['childExitCode']==0 and rows[-1]['fallback'] is False
u=next(x for x in rows if x['kind']=='unobserved-child-exit');assert u['pid']==3455925 and u['status']==0
report={'passed':True,'nativeAcceptance':False,'actualNativePassed':False,'recordedPassedChecks':9,'primaryError':m['primaryError'],'dispatcherExit':7,'dispatcherStdout':stdout,'unobservedExit':u,'topLevelCleanupInconsistent':True,'privateActivationCleanupPassed':False,'remainingDescendants':h['remainingDescendants'],'runtimeGone':h['runtimeGone']}
inputs=[n/'report.json',n/'native-evidence/host-evidence.json',ipc/'record.json',ipc/'stdout',p,o/'qa/native.py',o/'qa/activation-supervisor.py']
report['inputs']={str(p):sha(p) for p in inputs}
out=r/'qa'/('diagnose-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
(r/'component-manifest.json').write_text(json.dumps({'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Independent actual263 dispatcher/activation-cleanup failure diagnosis','files':files,'externalFiles':report['inputs'],'verificationReport':str((out/'report.json').relative_to(r))},indent=2)+'\n')
print(json.dumps({'manifestSHA256':sha(r/'component-manifest.json'),'report':str(out/'report.json'),'nativeAcceptance':False}))

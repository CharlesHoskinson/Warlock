"""Preserve actual failed bootstrap and independently characterize wire mismatch."""
import hashlib,importlib.util,json,resource,sys,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parent/'elm-gtk-role-native-v238'
REVIEW=ROOT.parent/'elm-gtk-bootstrap-source-review-v249'
RUN=BASE/'qa/native-1791141503469881852'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out=ROOT/'qa'/('verify-'+str(time.time_ns()));out.mkdir()
r={'passed':False,'failureConfirmed':False,'nativeAcceptance':False,'fullCampaignPassed':False,'inputs':{},'checks':[]}
try:
 for p,d in [(BASE/'component-manifest.json','c78433384efdb42aafee3eddc7375c11904ba8d4f43ed3fb04c7e07abfd505c2'),(REVIEW/'component-manifest.json','4f739faf2860b4794aad1f9d5c2add7e12bbad8f64695cbcd619995f35fdf162')]:
  assert sha(p)==d;r['inputs'][str(p)]=d
 p=RUN/'report.json';r['inputs'][str(p)]=sha(p);d=json.loads(p.read_text())
 for name,digest in d['artifacts'].items():
  p=RUN/name;assert sha(p)==digest,name;r['inputs'][str(p)]=digest
 assert d['passed'] is False and d['nativeAcceptance'] is False and d['fullCampaignPassed'] is False
 assert len(d['checks'])==8 and all(c['passed'] is True for c in d['checks'])
 assert 'six-second stage deadline' in d['primaryError']
 assert d['failureCleanupObserverUnload']=='ok' and d['failureCleanupAuthorityUnload']=='ok'
 cleanup=d['cleanup'];assert cleanup['runtimeGone'] is True and cleanup['remainingDescendants']==[] and cleanup['cleanupErrors']==[]
 assert len(cleanup['unexpectedInnerDescendants'])==10 and d['cleanupPassed'] is False
 sys.path.insert(0,str(BASE/'qa'))
 from protocol import Trace
 raw=(RUN/'native-evidence/gtk-role-client/wayland.log').read_bytes()
 trace=Trace(raw);assert len(trace.calls)==0
 assert b'{Default Queue}' in raw and b'{mesa vk display queue}' in raw and b'[19:18:30.' in raw
 rows=[json.loads(line) for line in (RUN/'native-evidence/gtk-role-client/journal.jsonl').read_text().splitlines()]
 mapped={row['role']:row['surfaceId'] for row in rows if row.get('event')=='map'}
 assert mapped=={'A':42,'C':71}
 bus=(RUN/'native-evidence/privateBus.log').read_text()
 assert "Activating service name='org.freedesktop.portal.Desktop'" in bus
 assert "Activating service name='org.a11y.Bus'" in bus
 r.update(passed=True,failureConfirmed=True,verifiedArtifacts=len(d['artifacts']),wireBytes=len(raw),parsedCalls=len(trace.calls),mappedGtkRoles=mapped,checks=['exact-held-source-review-binding','all-failure-artifacts','eight-actual-native-map-load-guards','original-six-second-failure','actual-zero-parser-calls-despite-mapped-GTK','cleanup-removal-with-unaccepted-unregistered-descendants'])
except BaseException as e:r['error']=repr(e)
finally:
 r['verifierSHA256']=sha(Path(__file__));(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(out/'report.json')
raise SystemExit(0 if r['passed'] else 1)

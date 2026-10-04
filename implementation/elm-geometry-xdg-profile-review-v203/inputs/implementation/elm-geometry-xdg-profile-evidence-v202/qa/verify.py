import hashlib,json,time
from pathlib import Path
root=Path('/home/hoskinson/omarchy-windows-parity');p=Path(__file__).resolve().parents[1];out=p/'qa'/('verify-'+str(time.time_ns()));out.mkdir();source=root/'implementation/elm-geometry-xdg-origin-native-v196/qa/native-1791130292488706555/report.json';r=json.loads(source.read_text());files={}
def verify(path,expected=None):
 f=Path(path);data=f.read_bytes();sha=hashlib.sha256(data).hexdigest();assert expected is None or sha==expected,str(f);files[str(f)]={'sha256':sha,'size':len(data)}
verify(source)
assert r['passed'] and r['cleanupPassed'] and len(r['checks'])==144 and all(c['passed'] for c in r['checks'])
assert r['profileCleanupErrors']==[] and r['finalCleanupErrors']==[]
assert {x['name'] for x in r['profiles']}=={f'{kind}-scale{s}' for kind in ['zero','origin','finite','fixed'] for s in [1,2]}
for path,sha in r['inputs'].items():verify(path,sha)
for rel,sha in r['artifacts'].items():verify(source.parent/rel,sha)
for name in ['elm-geometry-xdg-origin-native-v196','elm-geometry-xdg-hint-choice-fixture-v197','elm-geometry-xdg-hint-choice-review-v199','elm-geometry-client-journal-v194','elm-geometry-client-journal-review-v195']:
 verify(root/'implementation'/name/'component-manifest.json')
report={'evidenceIntegrityPassed':True,'files':files,'boundedXdgProfileCampaignPassed':True,'checks':144,'profiles':sorted({x['name'] for x in r['profiles']}),'cleanupPassed':True,'fullNativeAcceptance':False,'pixelAcceptance':False,'physicalInputAcceptance':False,'monitorScale2Acceptance':False,'GTKAcceptance':False,'releaseAcceptance':False,'scope':'Actual196 eight controlled XDG hint/origin/buffer-scale profiles; direct endpoint/native/configure-ACK-commit only'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'verifiedFiles':len(files),'checks':144,'boundedCampaignPassed':True}))

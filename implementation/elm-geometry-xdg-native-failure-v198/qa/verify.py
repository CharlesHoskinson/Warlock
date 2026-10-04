import hashlib,json,time
from pathlib import Path
p=Path(__file__).resolve().parents[1];source=p.parent/'elm-geometry-xdg-origin-native-v190/qa/native-1791129297579795954/report.json';d=json.loads(source.read_text());out=p/'qa'/('verify-'+str(time.time_ns()));out.mkdir();files={}
def record(f,expected=None):
 data=f.read_bytes();sha=hashlib.sha256(data).hexdigest();assert expected is None or sha==expected,str(f);files[str(f)]={'sha256':sha,'size':len(data)}
record(source)
for rel,sha in d['artifacts'].items():record(source.parent/rel,sha)
assert d['passed'] is False and d['cleanupPassed'] is True
assert all(c['passed'] for c in d['checks'])
finite=[json.loads(line) for line in (source.parent/'native-evidence/finite-scale1.jsonl').read_text().splitlines()]
assert [r['event'] for r in finite]==['configure','ack-configure','refused']
assert finite[0]['configuredWidth']==800 and finite[0]['configuredHeight']==600 and finite[-1]['reason']=='buffer-byte-bound'
for rel in ['elm-geometry-xdg-origin-native-v190/component-manifest.json','elm-geometry-xdg-origin-fixture-v184/component-manifest.json','elm-geometry-client-journal-v194/component-manifest.json','elm-geometry-client-journal-review-v195/component-manifest.json']:record(p.parent/rel)
report={'evidenceIntegrityPassed':True,'files':files,'nativeCampaignPassed':False,'cleanupPassed':True,'recordedPassingChecks':len(d['checks']),'completedProfiles':['zero-scale1','origin-scale1'],'failure':'finite-scale1 ordinary proposal800x600 rejected by strict fixture against400x300 hint; cleanup parser masks causal error','fullNativeAcceptance':False,'scope':'Failure evidence/source integrity; partial native paths do not accept full campaign'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'verifiedFiles':len(files),'campaignPassed':False,'cleanupPassed':True,'checks':len(d['checks'])}))

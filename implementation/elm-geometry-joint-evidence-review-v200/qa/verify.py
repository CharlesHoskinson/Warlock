import json,hashlib,time
from pathlib import Path
root=Path('/home/hoskinson/omarchy-windows-parity');p=Path(__file__).resolve().parents[1];out=p/'qa'/('review-'+str(time.time_ns()));out.mkdir();records={}
def verify(path,expected=None):
 f=Path(path);data=f.read_bytes();sha=hashlib.sha256(data).hexdigest();assert expected is None or sha==expected,str(f);records[str(f)]={'sha256':sha,'size':len(data)}
manifest=root/'implementation/elm-geometry-joint-held-v434/qa/slice-manifest.json';d=json.loads(manifest.read_text());verify(manifest);verify(d['parentManifest'],d['parentManifestSHA256'])
for row in d['files']:verify(root/row['path'],row['sha256'])
for row in d['reports']:
 verify(root/row['path'],row['sha256']);assert json.loads((root/row['path']).read_text())['passed']==row['passed']
path=root/'implementation/elm-geometry-lifetime-retirement-native-v432/qa/native-1791129443414985239/report.json';r=json.loads(path.read_text())
assert r['passed'] and r['cleanupPassed'] and len(r['checks'])==161 and all(x['passed'] for x in r['checks'])
assert r['scenarios']==[f'GEOMETRY-MENU-{i:02}' for i in range(1,11)]
assert r['receiptHold09']['finishedBeforeDeadline'] and r['receiptHold09']['deadlineSeconds']==6
assert r['reconnectFixture']['deadlineSeconds']==6 and r['retirementAddressDiagnostic']['addressReused'] is False
assert not r['allContractScenariosPassed'] and not r['fullRoadmapAccepted']
for row in r['pair'].values():verify(row['path'],row['sha256'])
report={'evidenceIntegrityPassed':True,'files':records,'nativeEvidenceReviewed':True,'executedChecks':161,'scenarioIds':r['scenarios'],'scope':'Independent frozen434/432 evidence/source integrity and bounded scenario review; no native rerun or full scenario refinement proof','retirementOracleAmended':True,'forcedSameAddressABAIn432':False,'fullGeometryAccepted':False,'fullRoadmapAccepted':False,'releaseAccepted':False}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'verifiedFiles':len(records),'executedChecksReviewed':161}))

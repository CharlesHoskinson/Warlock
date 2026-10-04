import datetime,hashlib,json,resource
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];GUI=ROOT.parent/'elm-launcher-focus-v59';assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
reports={}
for pattern in ['build-*','checks-*','model-*']:
 p=sorted((GUI/'qa').glob(pattern+'/report.json'))[-1];v=json.loads(p.read_text());assert v['passed']
 if 'inputs' in v:assert all(sha(GUI/rel)==digest for rel,digest in v['inputs'].items())
 else:assert sha(GUI/'spec/view.qnt')==v['sourceSHA256']
 reports[str(p.relative_to(GUI))]={'passed':True,'sha256':sha(p),'checks':len(v.get('checks',[])),'typedChecks':v.get('typedChecks'),'namedScenarios':v.get('namedScenarios'),'invariantSamples':v.get('invariantSamples')}
parent=GUI.parent/'elm-launch-controller-v56'; inherited=['elm.json','src/Catalog.elm','src/Launch.elm','src/LaunchReplay.elm','src/UInt64.elm']
assert all(sha(GUI/name)==sha(parent/name) for name in inherited)
old=json.loads((parent/'qa/slice-manifest.json').read_text());assert old['passed']
assert all(sha(parent/name)==old['files'][name] for name in inherited)
inheritance={'passed':True,'scope':'V56 compiled33 inherited by identical inputs only; historical abstract Quint context not new Desktop refinement','parentManifest':str(parent/'qa/slice-manifest.json'),'parentSHA256':sha(parent/'qa/slice-manifest.json'),'files':{name:sha(GUI/name) for name in inherited},'compiledChecks':33}
(GUI/'qa/inherited-launch-receipt.json').write_text(json.dumps(inheritance,indent=2)+'\n')
assert sha(GUI/'adapter/taskbar_catalog.py')==sha(GUI.parent/'elm-catalog-launch-v55/native/taskbar_catalog.py')
assert sha(GUI/'adapter/catalog_authority.py')==sha(GUI.parent/'elm-catalog-launch-v55/native/catalog_authority.py')
packets=sorted((ROOT/'qa').glob('native-*/report.json'));assert len(packets)==3
previous=json.loads((ROOT.parent/'elm-picker-parent-native-v54/qa/native-1791074500386436249/report.json').read_text())
first=json.loads(packets[0].read_text());assert [c['name'] for c in first['checks']]==[c['name'] for c in previous['checks']]
old_launch=json.loads((ROOT.parent/'elm-launch-native-v58/qa/native-1791076788726236476/report.json').read_text())
assert [c['name'] for c in json.loads(packets[1].read_text())['checks']]==[c['name'] for c in old_launch['checks']]
transport=GUI.parent/'elm-launch-host-v57/qa/transport-1791076844381796481/report.json';original=json.loads(transport.read_text());assert original['passed']
assert all(sha(GUI/rel)==digest for rel,digest in original['inputs'].items())
(GUI/'qa/inherited-transport-receipt.json').write_text(json.dumps({'passed':True,'checks':17,'report':str(transport),'sha256':sha(transport),'scope':'Transport17 inherited only by identical inputs','inputs':original['inputs']},indent=2)+'\n')
for p in packets:
 v=json.loads(p.read_text());assert v['passed'] and v['cleanupPassed'] and all(c['passed'] for c in v['checks'])
 assert sha(v['buildReport'])==v['buildReportSHA256']
 for artifact in v['pair'].values():assert sha(artifact['path'])==artifact['sha256']
 assert all(sha(name)==digest for name,digest in v['inputs'].items())
 reports[str(p)]={'passed':True,'sha256':sha(p),'checks':len(v['checks']),'cleanupPassed':True}
for directory,scope in [(GUI,'Compiled scoped launcher focus and view retirement; native acceptance inV60'),(ROOT,'Native91 and launcher17 original identities/order plus keyboard26; not production/release acceptance')]:
 manifest={'passed':True,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':scope,'wholeFeatureAccepted':False,'completedRequirementIds':[],'reports':reports,'files':{str(p.relative_to(directory)):sha(p) for p in sorted(directory.rglob('*')) if p.is_file() and p.name!='slice-manifest.json'}}
 (directory/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(directory/'qa/slice-manifest.json')

import hashlib,json,time
from pathlib import Path
p=Path(__file__).resolve().parents[1];out=p/'qa'/('verify-'+str(time.time_ns()));out.mkdir();records={}
def verify(path,expected):
 f=Path(path);sha=hashlib.sha256(f.read_bytes()).hexdigest();assert sha==expected,str(f);records[str(f)]=sha
meta=json.loads((p/'native-build-report.json').read_text())
for path,sha in [(meta['binary'],meta['sha256']),(meta['plugin']['path'],meta['plugin']['sha256']),(meta['pluginBuildReport'],meta['pluginBuildReportSHA256']),(meta['linkClosureReport'],meta['linkClosureReportSHA256']),(meta['coreComponentManifest'],meta['coreComponentManifestSHA256'])]:verify(path,sha)
d=json.loads(Path(meta['pluginBuildReport']).read_text());assert d['passed'] and not d['missingSymbols'] and d['core']['path']==meta['binary'] and d['core']['sha256']==meta['sha256']
for path,sha in d['dependencies'].items():verify(path,sha)
for rel,sha in d['inputs'].items():verify(Path(meta['pluginBuildReport']).parent/'inputs'/rel,sha)
aq=json.loads((p/'aq-tuple.json').read_text());verify(aq['manifest'],aq['manifestSHA256']);verify(aq['library'],aq['librarySHA256'])
origin=json.loads((p/'origin.json').read_text());verify(origin['oldPairManifest'],origin['oldPairManifestSHA256'])
parent=Path(origin['parent']);assert (p/'candidate_host.py').read_bytes()==(parent/'candidate_host.py').read_bytes()
assert (p/'aq-tuple.json').read_bytes()==(parent/'aq-tuple.json').read_bytes()
assert (p/'parent-probe-build.json').read_bytes()==(parent/'parent-probe-build.json').read_bytes()
report={'passed':True,'sourceIntegrityVerified':True,'verifiedFiles':len(records),'files':records,'pair':{'core':meta['binary'],'plugin':meta['plugin']['path'],'aquamarine':aq['library']},'nativeAcceptance':False,'scope':'Prepared owning producer tuple; unchanged host/source checks, no import/load/GUI or consumer qualification'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'verifiedFiles':len(records),'passed':True}))

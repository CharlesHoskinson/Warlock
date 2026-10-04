import hashlib,json,resource,stat
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
origin=json.loads((ROOT/'origin.json').read_text());assert sha(ROOT/'original/activation-supervisor.py')==origin['sha256']
p=ROOT/'qa/witness-1791143159542714586/report.json';d=json.loads(p.read_text())
assert d['passed'] is True and d['unsafeWitnessConfirmed'] is True and d['nativeAcceptance'] is False
assert d['sourceSHA256']==origin['sha256'] and d['testSHA256']==sha(ROOT/'qa/test.py')
assert len(d['cases'])==2 and all(c['passed'] is True and c['failureCleanupSignals']==[] and not Path(c['runtime']).exists() for c in d['cases'])
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
(ROOT/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'unsafeWitnessConfirmed':True,'nativeAcceptance':False,'fullCampaignPassed':False,'scope':'actual pre-fix supervisor CPU setsid failure, no GUI','files':files},indent=2)+'\n');print(ROOT/'component-manifest.json')

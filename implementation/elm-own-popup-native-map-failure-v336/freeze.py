import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
p=ROOT/'analysis-1791159282954963705/report.json';r=json.loads(p.read_text());assert r['passed'] and r['actualConflictingPathnameIdentified'] is False and r['failingRawMapsPresent'] is False
for path,row in r['externalFiles'].items():assert sha(path)==row['sha256'],path
own={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='component-manifest.json' and '__pycache__' not in p.parts}
m={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'ownBlockerGrantQualified':False,'fullGTKCampaignPassed':False,'nativeCampaignPassed':False,'cleanupPassed':True,'actualConflictingPathnameIdentified':False,'scope':'Failure332 full retained outcome/source evidence; missing failing raw maps prevents specific conflicting-name diagnosis','files':own,'externalFiles':r['externalFiles'],'analysisReport':str(ROOT/'analysis-1791159282954963705/report.json')}
(ROOT/'component-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('PASS',len(own),'own',len(r['externalFiles']),'external',sha(ROOT/'component-manifest.json'))

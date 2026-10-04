"""Freeze exact Qt journal source, synthetic tests and compiled enum closure."""
import hashlib,json,resource,stat,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not (ROOT/'component-manifest.json').exists()
 out=ROOT/'qa'/('freeze-'+str(time.time_ns()));out.mkdir()
 report={'passed':False,'nativeAcceptance':False}
 try:
  path=sorted((ROOT/'qa').glob('test-*/report.json'))[-1]
  test=json.loads(path.read_text());assert test['passed']
  assert sha(ROOT/'qa/journal.py')==test['sourceSHA256']==sha(path.parent/'journal.py')
  assert sha(ROOT/'qa/test.py')==sha(path.parent/'test.py')
  assert sha(path.parent/'enums.cpp')==test['enumSourceSHA256']
  assert sha(path.parent/'enums')==test['enumBinarySHA256']
  external=dict(test['externalFiles'])
  origin=json.loads((ROOT/'origin.json').read_text())
  assert sha(origin['parserParent'])==origin['parserParentSHA256']==sha(ROOT/'ancestor-journal.py')
  external[origin['parserParent']]=origin['parserParentSHA256']
  for p,h in external.items():assert sha(p)==h,p
  report.update(passed=True,tests=str(path),testsSHA256=sha(path),checks=len(test['checks']),verifiedExternalFiles=len(external))
 finally:
  (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
 if report['passed']:
  files={}
  for p in sorted(ROOT.rglob('*')):
   assert not p.is_symlink(),p
   if p.is_file():files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
  manifest={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Qt strict DTO consumer and actual compiled enum closure; synthetic input only','files':files,'externalFiles':external,'verificationReport':str(out/'report.json')}
  (ROOT/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())

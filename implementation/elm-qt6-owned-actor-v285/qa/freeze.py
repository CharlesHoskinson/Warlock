"""Exact actor/journal/producer and protected CPU subprocess evidence closure."""
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
 report={'passed':False,'nativeAcceptance':False};external={}
 def pin(p,h=None):
  p=Path(p);actual=sha(p);assert h is None or actual==h,p;external[str(p.resolve())]=actual
 def manifest(directory):
  directory=Path(directory);path=directory/'component-manifest.json';r=json.loads(path.read_text());assert r['sourceHeld'] and r['evidenceIntegrityPassed'];pin(path)
  for name,row in r['files'].items():
   p=directory/name;assert not p.is_symlink() and p.stat().st_size==row['size'];pin(p,row['sha256'])
   if 'mode' in row:assert stat.S_IMODE(p.stat().st_mode)==(int(row['mode'],8) if isinstance(row['mode'],str) else row['mode'])
  for p,h in r.get('externalFiles',{}).items():pin(p,h if isinstance(h,str) else h['sha256'])
 try:
  origin=json.loads((ROOT/'origin.json').read_text())
  pin(origin['actorParent'],origin['actorParentSHA256']);assert sha(ROOT/'ancestor-actor.py')==origin['actorParentSHA256']
  pin(origin['journalParent'],origin['journalParentSHA256']);assert sha(ROOT/'qa/journal.py')==origin['journalParentSHA256']
  manifest(Path(origin['journalManifest']).parent);manifest(origin['fixture'])
  build=json.loads((Path(origin['fixture'])/'client-build-report.json').read_text());assert build['passed']
  pin(build['artifact']['path'],build['artifact']['sha256'])
  for group in ('dependencies','libraries','tools'):
   for p,row in build[group].items():pin(p,row['sha256'])
  reports=[]
  for glob in ('actor-*/report.json','commands-*/report.json'):
   path=sorted((ROOT/'qa').glob(glob))[-1];r=json.loads(path.read_text());assert r['passed'] and r['nativeAcceptance'] is False
   for p,h in r['inputs'].items():assert sha(p)==h,p
   for p,h in r.get('externalFiles',{}).items():pin(p,h)
   if glob.startswith('commands'):
    assert sha(path.parent/'grammar')==r['grammarBinarySHA256'] and sha(path.parent/'grammar.cpp')==r['grammarSourceSHA256']
    assert sha(path.parent/'commands.hpp')==r['owningCommandsSHA256']
   reports.append({'path':str(path),'sha256':sha(path),'checks':len(r['checks'])})
  report.update(passed=True,reports=reports,verifiedExternalFiles=len(external))
 finally:
  (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
 if report['passed']:
  files={}
  for p in sorted(ROOT.rglob('*')):
   assert not p.is_symlink(),p
   if p.is_file():files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
  result={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Qt owned actor with synthetic producer journals, real subprocesses/pipe backpressure and compiled owning C++ command decoder only','files':files,'externalFiles':external,'verificationReport':str(out/'report.json')}
  (ROOT/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
 return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
